#include <unistd.h>

#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <thread>
#include <algorithm>

#define END_OF_URI_LIST "END_OF_URI_LIST"

#define DEFAULT_MQTT_HOST "127.0.0.1"
#define DEFAULT_MQTT_PORT 1883

std::string MQTT_HOST = DEFAULT_MQTT_HOST;
int MQTT_PORT = DEFAULT_MQTT_PORT;
std::string MQTT_TOPIC = "/device";

class Device
{
public:
    std::string device_name;
    std::vector<std::string> uri_list;

    Device(std::string _device_name, std::vector<std::string> _uri_list) : device_name(_device_name),
                                                                           uri_list(_uri_list) {}
};

std::vector<Device> device_list;

/******************************************************************************************************/

void sleep_msecs(const float _time)
{
    struct timespec sleepTime;
    sleepTime.tv_sec = 0;
    sleepTime.tv_nsec = static_cast<long>(_time * 1000000000); // nanoseconds

    int result = nanosleep(&sleepTime, NULL);
}

void command_sys(const std::string &_command)
{
    std::system(_command.c_str());
}

void runCommand_system(const std::string &_command, const std::vector<std::string> _argv)
{
    std::string command_with_args;

    std::stringstream ss;
    ss << _command << " ";
    for (std::string arg : _argv)
        ss << arg << " ";

    command_with_args = ss.str();
    command_with_args.pop_back();

    std::thread thr(command_sys, command_with_args); // Create a new thread to run the command

    thr.detach(); // Detach the thread to run independently
}

void sendMessageToMQTTServer(std::string _host,
                             int _port,
                             std::string _topic,
                             std::string _message)
{
    std::string cmd = "mosquitto_pub";
    std::vector<std::string> argv;

    argv.push_back("-h");
    argv.push_back(_host);

    argv.push_back("-p");
    argv.push_back(std::to_string(_port));

    argv.push_back("-t");
    argv.push_back(_topic);

    argv.push_back("-m");
    std::stringstream ss;
    ss << "\"" << _message << "\"";
    argv.push_back(ss.str());

    try
    {
        runCommand_system(cmd, argv);
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }
}

std::string createMessage(const Device &_dev)
{
    std::string message;
    std::stringstream ss;
    ss << _dev.device_name;
    for (const auto &uri : _dev.uri_list)
        ss << "_" << uri;
    message = ss.str();
    return message;
}

std::string getURI(const std::string &_line)
{
    size_t slash_pos = _line.find("/");
    if (slash_pos == std::string::npos)
        return END_OF_URI_LIST;

    std::string uri = _line.substr(slash_pos, _line.size() - 1);

    return uri;
}

bool getDevicesList()
{
    std::string command = "v4l2-ctl --list-device";
    FILE *pipe = popen(command.c_str(), "r");
    if (!pipe)
        return false;

    char buffer[4096];
    while (fgets(buffer, 4096, pipe))
    {
        std::string line = std::string(buffer);
        line.pop_back(); // Remove new-line character
        size_t pos = line.find("usb-0000");
        std::string device_name;

        if (pos != std::string::npos)
        {
            device_name = line.substr(0, pos - 2);

            std::string uri;
            std::vector<std::string> uri_list;

            while (uri != END_OF_URI_LIST)
            {
                fgets(buffer, 4096, pipe);
                std::string line = std::string(buffer);
                line.pop_back(); // Remove new-line character
                uri = getURI(line);
                if (uri != END_OF_URI_LIST)
                    uri_list.push_back(uri);
            }

            Device new_device = Device(device_name, uri_list);
            device_list.push_back(new_device);
        }
    }

    return true;
}

void debug()
{
    for (const auto &device : device_list)
    {
        std::cout << std::endl
                  << device.device_name << std::endl;
        for (const auto &uri : device.uri_list)
            std::cout << uri << std::endl;
    }

    std::cout << "\nSize of device list: " << device_list.size() << std::endl;
}

int main(int argc, char *argv[])
{
    if (argc != 4)
    {
        std::cerr << "Usage: " << std::string(argv[0]) << " MQTT_host MQTT_port MQTT_topic" << std::endl;
        return -1;
    }
    MQTT_HOST = std::string(argv[1]);
    MQTT_PORT = std::stoi(std::string(argv[2]));
    MQTT_TOPIC = std::string(argv[3]);

    ////////////////////////////////

    if (!getDevicesList())
        return -1;

    for (const auto &device : device_list)
    {
        std::string message = createMessage(device);
        sendMessageToMQTTServer(MQTT_HOST, MQTT_PORT, MQTT_TOPIC, message);
        sleep_msecs(0.1);
    }

    return 0;
}