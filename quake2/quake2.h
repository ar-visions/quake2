#ifndef QUAKE2_NET_H
#define QUAKE2_NET_H
#include <stdint.h>
// udp socket, not blocking; -1 when it cannot be made
int      q2net_open   (int port);
void     q2net_close  (int fd);
int      q2net_send   (int fd, uint32_t ip, int port, uint8_t* data, int len);
// one waiting packet into buf; 0 when there is none
int      q2net_recv   (int fd, uint8_t* buf, int max, uint32_t* ip, int* port);
// a host name or dotted address; 0 when unknown
uint32_t q2net_resolve(char* host);
#endif
