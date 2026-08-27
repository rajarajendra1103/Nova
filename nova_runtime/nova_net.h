#ifndef NOVA_NET_H
#define NOVA_NET_H

#include <stdbool.h>

// ============================================================
// MULTIPLAYER & GAME NETWORKING TYPES
// ============================================================
typedef struct {
    int port;
    int maxClients;
    int clientCount;
    bool isRunning;
} NovaNetHost;

typedef struct {
    char host[64];
    int port;
    bool isConnected;
    float pingMs;
} NovaNetClient;

// Network Host API
NovaNetHost novaNetHostNew(int port, int maxClients);
void novaNetHostStart(NovaNetHost* host);
void novaNetHostStop(NovaNetHost* host);
void novaNetBroadcast(const char* channel, const char* data);
void novaNetSend(const char* clientId, const char* channel, const char* data);
void novaNetRPCCall(const char* rpcName, const char* payload);
void novaNetReplicate(const char* stateName, int entityId, const char* data);

// Network Client API
NovaNetClient novaNetClientNew(const char* host, int port);
void novaNetClientConnect(NovaNetClient* client);
void novaNetClientSend(NovaNetClient* client, const char* channel, const char* data);
void novaNetClientDisconnect(NovaNetClient* client);

#endif // NOVA_NET_H
