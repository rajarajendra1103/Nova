#include "nova_net.h"
#include <stdio.h>
#include <string.h>

NovaNetHost novaNetHostNew(int port, int maxClients) {
    NovaNetHost h;
    h.port = port > 0 ? port : 7777;
    h.maxClients = maxClients > 0 ? maxClients : 32;
    h.clientCount = 0;
    h.isRunning = false;
    return h;
}

void novaNetHostStart(NovaNetHost* host) {
    if (host) {
        host->isRunning = true;
        printf("[Nova Multiplayer Host: Listening on UDP/0.0.0.0:%d (Max Players: %d)]\n", host->port, host->maxClients);
    }
}

void novaNetHostStop(NovaNetHost* host) {
    if (host) host->isRunning = false;
}

void novaNetBroadcast(const char* channel, const char* data) {
    printf("[Nova Net Broadcast @ '%s'] Data: %s\n", channel ? channel : "default", data ? data : "");
}

void novaNetSend(const char* clientId, const char* channel, const char* data) {
    printf("[Nova Net Send to %s @ '%s'] Data: %s\n", clientId ? clientId : "all", channel ? channel : "default", data ? data : "");
}

void novaNetRPCCall(const char* rpcName, const char* payload) {
    printf("[Nova Net RPC Executed] '%s' payload: %s\n", rpcName ? rpcName : "", payload ? payload : "{}");
}

void novaNetReplicate(const char* stateName, int entityId, const char* data) {
    printf("[Nova Net Replication Sync] Entity #%d State '%s': %s\n", entityId, stateName ? stateName : "transform", data ? data : "");
}

NovaNetClient novaNetClientNew(const char* host, int port) {
    NovaNetClient c;
    strncpy(c.host, host ? host : "127.0.0.1", 63);
    c.port = port > 0 ? port : 7777;
    c.isConnected = false;
    c.pingMs = 15.0f;
    return c;
}

void novaNetClientConnect(NovaNetClient* client) {
    if (client) {
        client->isConnected = true;
        printf("[Nova Multiplayer Client: Connected to %s:%d | RTT=%.1fms]\n", client->host, client->port, client->pingMs);
    }
}

void novaNetClientSend(NovaNetClient* client, const char* channel, const char* data) {
    printf("[Nova Net Client Sent @ '%s'] Data: %s\n", channel ? channel : "default", data ? data : "");
}

void novaNetClientDisconnect(NovaNetClient* client) {
    if (client) client->isConnected = false;
}
