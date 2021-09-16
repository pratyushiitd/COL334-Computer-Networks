#include <iostream>
#include <string>
#include <regex>
#include <fstream>
#include <arpa/inet.h>

using namespace std;

string host_do;
regex ipv4("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}");
string command(int host);

std::string exec(const char* cmd) {
    char buffer[1024];
    std::string result = "";
    FILE* pipe = popen(cmd, "r");
    if (!pipe) throw std::runtime_error("popen() failed!");
    try {
        while (fgets(buffer, sizeof buffer, pipe) != NULL) {
            result += buffer;
        }
    } catch (...) {
        pclose(pipe);
        throw;
    }
    pclose(pipe);
    return result;
}
pair<string,bool> get_ip(string str)
{
    string word = "";
    vector<string> ip_add;
    bool end = true;
    for (char x : str) 
    {
        if (x == ' '){
            //cout << word << endl;
            if (std::regex_match(word, ipv4))ip_add.push_back(word);
            if (word.rfind("exceeded", 0) == 0)
            {
                end = false;
            }
            word = "";
        }
        else {
            if (x!=':') word = word + x;
        }
    }
    //cout << ip_add.size() << endl;
    if (ip_add.size() > 0)return make_pair(ip_add[0], end);
    return make_pair("",false);
}
double get_time(string str)
{
    string word = "";
    for (char x : str) 
    {
        if (x == ' '){
            //cout << word << endl;
            if (word.rfind("time=", 0) == 0)
            {
                //cout << word << endl;
                return stof(word.substr(5));
            }
            word = "";
        }
        else {
            if (x!=':') word = word + x;
        }
    }
    //cout << ip_add.size() << endl;
    return 0.0;
}
string ping_cmd(string host, int count, int ttl)
{
    string strg = "ping -c " + to_string(count) + " -m " + to_string(ttl) + " " + host_do;
    return strg.c_str();
}
int main(int argc, char *argv[])
{
    if (argc > 2)
    {
        printf("Additional arguements provided\n");return 0;
    }
    else if (argc == 2)
    {
        host_do = argv[1];
    }
    else host_do = "www.iitd.ac.in";
    string st = "";int ttl = 1; double rtt = 0;
    bool dest_reached = false;
    vector<double> RTT_vals;
    vector<double> hops;
    fstream my_file;
    my_file.open("res/rtt_vals.txt", ios::out);
    while(!dest_reached){
        pair<string, bool> p = get_ip(exec(ping_cmd(host_do, 1, ttl).c_str()));
        st = p.first;
        dest_reached = p.second;
        rtt = 0.0;
        if (st.length() > 0)
        {
            rtt = get_time(exec(ping_cmd(st, 1, 64).c_str()));
            rtt = min(rtt, get_time(exec(ping_cmd(st, 1, 64).c_str())));
            rtt = min(rtt, get_time(exec(ping_cmd(st, 1, 64).c_str())));
        }
        printf("%d \t RTT = %06.3fms \t IPv4 = %s\n", ttl, rtt, st.c_str());
        //cout << dest_reached << ' ' << st << endl;
        my_file << rtt << '\n';
        hops.push_back((double)ttl);
        ttl++;
    }
    my_file.close();
    system("python3 res/plot.py");
	return 0;
}