#include "quake2.h"
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int q2net_open(int port) {
    int fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (fd < 0) return -1;
    int on = 1;
    setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &on, sizeof on);
    fcntl(fd, F_SETFL, fcntl(fd, F_GETFL, 0) | O_NONBLOCK);
    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_addr.s_addr = INADDR_ANY;
    a.sin_port        = htons((uint16_t)port);
    if (bind(fd, (struct sockaddr*)&a, sizeof a) < 0) { close(fd); return -1; }
    return fd;
}

void q2net_close(int fd) { if (fd >= 0) close(fd); }

int q2net_send(int fd, uint32_t ip, int port, uint8_t* data, int len) {
    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_addr.s_addr = ip;
    a.sin_port        = htons((uint16_t)port);
    return (int)sendto(fd, data, len, 0, (struct sockaddr*)&a, sizeof a);
}

int q2net_recv(int fd, uint8_t* buf, int max, uint32_t* ip, int* port) {
    struct sockaddr_in a;
    socklen_t n = sizeof a;
    int got = (int)recvfrom(fd, buf, max, 0, (struct sockaddr*)&a, &n);
    if (got <= 0) return 0;
    *ip   = a.sin_addr.s_addr;
    *port = ntohs(a.sin_port);
    return got;
}

uint32_t q2net_resolve(char* host) {
    struct in_addr in;
    if (inet_pton(AF_INET, host, &in) == 1) return in.s_addr;
    struct hostent* h = gethostbyname(host);
    if (!h || !h->h_addr_list[0]) return 0;
    uint32_t ip;
    memcpy(&ip, h->h_addr_list[0], 4);
    return ip;
}
