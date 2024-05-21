#!/usr/bin/env python3

from modules import *


pgie_classes_str = ["Person", "TwoWheeler", "Person", "RoadSign"]
perf_data = None
number_sources = None
global_frame_count = 0
frame_count = {}
saved_count = {}


def osd_sink_pad_buffer_probe(pad, info, u_data):
    """
    Extract metadata received on OSD sink pad and
    update params for drawing rectangle, object information, etc...
    """

    global global_frame_count

    frame_number = 0
    obj_counter = {
        config.PGIE_CLASS_ID_VEHICLE: 0,
        config.PGIE_CLASS_ID_PERSON: 0,
        config.PGIE_CLASS_ID_BICYCLE: 0,
        config.PGIE_CLASS_ID_ROADSIGN: 0
    }

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print(f"[ERROR] Unable to get GstBuffer \n")
        return

    # Retrieve batch metadata from the gst_buffer
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Cast to pyds.NvDsFrameMeta
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            continue

        frame_number = global_frame_count
        global_frame_count = global_frame_count + 1

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                continue

            # Update the object text display
            txt_params = obj_meta.text_params

            # Set display_text
            txt_params.display_text = pgie_classes_str[obj_meta.class_id]

            obj_counter[obj_meta.class_id] += 1

            # Font, font-color, font-size and text background color
            txt_params.font_params.font_name = "Serif"
            txt_params.font_params.font_size = 10
            txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
            txt_params.set_bg_clr = 1
            txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

            confidence = obj_meta.confidence

            # Message is being sent for Person object with confidence in range (MIN_CONFIDENCE, MAX_CONFIDENCE), after FRAMES_PER_MESSAGE frames
            if (config.MIN_CONFIDENCE < confidence < config.MAX_CONFIDENCE) and (frame_number % config.FRAMES_PER_MESSAGE == 0):

                # Allocating an NvDsEventMsgMeta instance and getting reference to it
                msg_meta = pyds.alloc_nvds_event_msg_meta()

                msg_meta.bbox.top = obj_meta.rect_params.top
                msg_meta.bbox.left = obj_meta.rect_params.left
                msg_meta.bbox.width = obj_meta.rect_params.width
                msg_meta.bbox.height = obj_meta.rect_params.height
                msg_meta.frameId = frame_number
                msg_meta.trackingId = long_to_uint64(obj_meta.object_id)
                msg_meta.confidence = obj_meta.confidence
                msg_meta = metadata.generate_event_msg_meta(
                    msg_meta, obj_meta.class_id)

                user_event_meta = pyds.nvds_acquire_user_meta_from_pool(
                    batch_meta)

                if user_event_meta:
                    user_event_meta.user_meta_data = msg_meta
                    user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META

                    # Setting callbacks in the event msg meta
                    pyds.user_copyfunc(
                        user_event_meta, metadata.meta_copy_func)
                    pyds.user_releasefunc(
                        user_event_meta, metadata.meta_free_func)
                    pyds.nvds_add_user_meta_to_frame(frame_meta,
                                                     user_event_meta)
                else:
                    print("[ERROR] in attaching event meta to buffer\n")

            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    print("Frame Number =", frame_number, "Vehicle Count =",
          obj_counter[config.PGIE_CLASS_ID_VEHICLE], "Person Count =",
          obj_counter[config.PGIE_CLASS_ID_PERSON])
    return Gst.PadProbeReturn.OK


def cb_newpad(decodebin, _decoder_src_pad, _data):
    """
    New pad callback function
    """

    caps = _decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = _data
    features = caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not audio.
    if (gstname.find("video") != -1):
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(_decoder_src_pad):
                sys.stderr.write(
                    "[ERROR] Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(
                "[ERROR] Decodebin did not pick nvidia decoder plugin.\n")


def decodebin_child_added(_child_proxy, _object, _name, _user_data):
    """
    Add child decodebin
    """

    print("[ INFO] Decodebin child added:", _name, "\n")
    if _name.find("decodebin") != -1:
        _object.connect("child-added", decodebin_child_added, _user_data)

    if "source" in _name:
        source_element = _child_proxy.get_by_name("source")
        if source_element.find_property('drop-on-latency') != None:
            _object.set_property("drop-on-latency", True)


def create_source_bin(_index, _uri):
    """
    Create sourcebin from a RTSP URI
    """

    # Create a source GstBin to abstract this bin's content from the rest of the pipeline
    bin_name = "source-bin-%02d" % _index
    print(bin_name)
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write("[ERROR] Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write("[ERROR] Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri", _uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(
        Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write("[ERROR] Failed to add ghost pad in source bin \n")
        return None
    return nbin


def tiler_sink_pad_buffer_probe(_pad, _info, _u_data):
    """
    Extract metadata received on tiler src pad
    and update params for drawing rectangle, object information etc.
    """

    global global_frame_count

    gst_buffer = _info.get_buffer()
    if not gst_buffer:
        print("[ERROR] Unable to get GstBuffer")
        return

    # Retrieve batch metadata from the gst_buffer
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # l_frame.data needs a cast to pyds.NvDsFrameMeta
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        l_obj = frame_meta.obj_meta_list
        obj_counter = {
            config.PGIE_CLASS_ID_VEHICLE: 0,
            config.PGIE_CLASS_ID_PERSON: 0,
            config.PGIE_CLASS_ID_BICYCLE: 0,
            config.PGIE_CLASS_ID_ROADSIGN: 0
        }

        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1

            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        # update frame rate through this probe
        stream_index = "stream{0}".format(frame_meta.pad_index)
        global perf_data
        perf_data.update_fps(stream_index)

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def args_parser(args):
    """
    Parse arguments to get URIs list
    """

    if len(args) < 2:
        sys.stderr.write(
            "Usage: %s <uri1> [uri2] ... [uriN]\n" % args[0])
        return False

    global perf_data
    global number_sources
    perf_data = PERF_DATA(len(args) - 1)
    number_sources = len(args) - 1

    return True


def main(args):
    global perf_data
    global number_sources
    global frame_count
    global saved_count

    #############################

    # Registering callbacks
    pyds.register_user_copyfunc(metadata.meta_copy_func)
    pyds.register_user_releasefunc(metadata.meta_free_func)

    # Standard GStreamer initialization
    Gst.init(None)

    #############################

    # Create Pipeline element that will form a connection of other elements
    print("[ INFO] Creating Pipeline \n")
    pipeline = Gst.Pipeline()
    is_live = False
    if not pipeline:
        sys.stderr.write("[ERROR] Unable to create Pipeline\n")

    #############################

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write("[ERROR] Unable to create NvStreamMux \n")

    pipeline.add(streammux)

    for i in range(number_sources):
        frame_count["stream_" + str(i)] = 0
        saved_count["stream_" + str(i)] = 0
        print("[ INFO] Creating source_bin ", i, " \n ")

        uri_name = args[i + 1]
        if uri_name.find("rtsp://") == 0:
            is_live = True

        source_bin = create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("[ERROR] Unable to create source bin\n")
        pipeline.add(source_bin)

        padname = "sink_%u" % i
        sinkpad = streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("[ERROR] Unable to create sink pad bin \n")

        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("[ERROR] Unable to create src pad bin \n")
        srcpad.link(sinkpad)

    #############################

    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write("[ERROR] Unable to create pgie \n")

    #############################

    # Add nvvidconv1 and caps to convert the frames to RGBA, which is easier to work with in Python.
    nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
    if not nvvidconv1:
        sys.stderr.write("[ERROR] Unable to create nvvidconv1 \n")

    caps2 = Gst.ElementFactory.make("capsfilter", "filter2")
    if not caps2:
        sys.stderr.write("[ERROR] Unable to get the caps filter2 \n")
    caps2.set_property(
        "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
    )

    #############################

    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write("[ERROR] Unable to create tiler \n")

    #############################

    nvvidconv2 = Gst.ElementFactory.make("nvvideoconvert", "convertor2")
    if not nvvidconv2:
        sys.stderr.write("[ERROR] Unable to create nvvidconv2 \n")

    #############################

    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write("[ERROR] Unable to create nvosd \n")

    #############################

    msgconv = Gst.ElementFactory.make("nvmsgconv", "nvmsg-converter")
    if not msgconv:
        sys.stderr.write("[ERROR] Unable to create msgconv \n")

    #############################

    msgbroker = Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")
    if not msgbroker:
        sys.stderr.write("[ERROR] Unable to create msgbroker \n")

    #############################

    # Create tee and 2 queues
    tee = Gst.ElementFactory.make("tee", "nvsink-tee")
    if not tee:
        sys.stderr.write("[ERROR] Unable to create tee \n")

    queue1 = Gst.ElementFactory.make("queue", "nvtee-que1")
    if not queue1:
        sys.stderr.write("[ERROR] Unable to create queue1 \n")

    queue2 = Gst.ElementFactory.make("queue", "nvtee-que2")
    if not queue2:
        sys.stderr.write("[ERROR] Unable to create queue2 \n")

    #############################

    # video convert for streaming
    nvvidconv_postosd = Gst.ElementFactory.make(
        "nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write("[ERROR] Unable to create nvvidconv_postosd \n")

    #############################

    # Make the encoder
    if config.CODEC == "H264":
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        print("Creating H264 Encoder")
    elif config.CODEC == "H265":
        encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
        print("Creating H265 Encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")

    encoder.set_property("bitrate", int(config.BITRATE))

    if is_aarch64():
        encoder.set_property("preset-level", 1)
        encoder.set_property("insert-sps-pps", 1)

    # Make the payload-encode video into RTP packets
    if config.CODEC == "H264":
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        print("Creating H264 rtppay")
    elif config.CODEC == "H265":
        rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
        print("Creating H265 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")

    #############################

    # Set propertie UDP sink for rtsp out
    udpsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write("[ERROR] Unable to create udpsink")

    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", udpsink_port_num)
    sink.set_property("async", False)
    sink.set_property("sync", 1)
    sink.set_property("render-delay", int(config.RTSP_OUT_DELAY_USECS))

    #############################

    if is_live:
        print("[INFO] Atleast one of the rtsp video sources is live \n")
        streammux.set_property('live-source', 1)

    streammux.set_property('width', config.MUXER_OUTPUT_WIDTH)
    streammux.set_property('height', config.MUXER_OUTPUT_HEIGHT)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout',
                           config.MUXER_BATCH_TIMEOUT_USEC)

    #############################

    pgie.set_property('config-file-path', config.PGIE_CONFIG_FILE)
    pgie_batch_size = pgie.get_property("batch-size")

    if (pgie_batch_size != number_sources):
        print(
            f"[ WARN] Overriding infer-config batch-size {pgie_batch_size}with number of sources {number_sources}\n")
        pgie.set_property("batch-size", number_sources)

    #############################

    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", config.TILED_OUTPUT_WIDTH)
    tiler.set_property("height", config.TILED_OUTPUT_HEIGHT)

    #############################

    msgconv.set_property('config', config.MSGCONV_CONFIG_FILE)
    msgconv.set_property('payload-type', config.MSGCONV_SCHEMA_TYPE)

    #############################

    msgbroker.set_property('config', config.AMQP_CONFIG_FILE)
    msgbroker.set_property('proto-lib', config.AMQP_LIB_FILE)

    #############################

    if not is_aarch64():
        # Use CUDA unified memory in the pipeline so frames
        # can be easily accessed on CPU in Python.
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        streammux.set_property("nvbuf-memory-type", mem_type)
        nvvidconv1.set_property("nvbuf-memory-type", mem_type)
        nvvidconv1.set_property("nvbuf-memory-type", mem_type)
        tiler.set_property("nvbuf-memory-type", mem_type)

    #############################

    print("[ INFO] Adding elements to Pipeline \n")
    pipeline.add(pgie)
    pipeline.add(nvvidconv1)
    # pipeline.add(filter2)
    pipeline.add(tiler)
    pipeline.add(nvvidconv2)
    pipeline.add(nvosd)
    pipeline.add(nvvidconv_postosd)
    pipeline.add(msgconv)
    pipeline.add(msgbroker)
    pipeline.add(tee)
    pipeline.add(queue1)
    pipeline.add(queue2)
    pipeline.add(caps2)
    pipeline.add(encoder)
    pipeline.add(rtppay)
    pipeline.add(sink)

    #############################

    print("[ INFO] Linking elements in the Pipeline \n")
    streammux.link(pgie)
    pgie.link(nvvidconv1)
    nvvidconv1.link(caps2)
    # nvvidconv1.link(tiler)
    caps2.link(tiler)
    tiler.link(nvvidconv2)
    nvvidconv2.link(nvosd)
    nvosd.link(tee)
    queue1.link(msgconv)
    msgconv.link(msgbroker)
    queue2.link(encoder)
    # queue2.link(nvvidconv_postosd)
    # nvvidconv_postosd.link(caps2)
    # caps2.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    sink_pad = queue1.get_static_pad("sink")
    tee_msg_pad = tee.get_request_pad('src_%u')
    tee_render_pad = tee.get_request_pad("src_%u")
    if not tee_msg_pad or not tee_render_pad:
        sys.stderr.write("[ERROR] Unable to get request pads\n")
    tee_msg_pad.link(sink_pad)
    sink_pad = queue2.get_static_pad("sink")
    tee_render_pad.link(sink_pad)

    #############################

    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    #############################

    # start steaming
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % int(config.RTSP_OUT_PORT)
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (udpsink_port_num, str(config.CODEC))
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory(config.RTSP_OUT_FACTORY, factory)

    print(
        f"\n[ INFO] Launched RTSP Streaming at rtsp://localhost:{config.RTSP_OUT_PORT}{config.RTSP_OUT_FACTORY}\n")

    #############################

    tiler_sink_pad = tiler.get_static_pad("sink")
    if not tiler_sink_pad:
        sys.stderr.write("[ERROR] Unable to get src pad \n")
    else:
        tiler_sink_pad.add_probe(
            Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe, 0)
        # perf callback function to print fps every 5 sec
        GLib.timeout_add(5000, perf_data.perf_print_callback)

    #############################

    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write("[ERROR] Unable to get sink pad of nvosd \n")
    else:
        osdsinkpad.add_probe(Gst.PadProbeType.BUFFER,
                             osd_sink_pad_buffer_probe, 0)

    #############################

    print("[ INFO] Starting pipeline... \n")
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    #############################

    # cleanup
    print("[INFO] Exiting app...\n")
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':

    ret = args_parser(sys.argv)
    if not ret:
        sys.exit(1)
    else:
        sys.exit(main(sys.argv))
