#ifndef NOVA_BACKEND_H
#define NOVA_BACKEND_H

#include <stdbool.h>

// ============================================================
// BACKEND SERVER & DATABASE TYPES
// ============================================================
typedef struct {
    int port;
    bool isRunning;
} NovaServer;

typedef struct {
    char dbPath[128];
    int rowCount;
} NovaDB;

typedef struct {
    char token[128];
    char user[64];
    bool isValid;
} NovaAuth;

typedef struct {
    char key[64];
    char value[256];
} NovaKV;

// Server
NovaServer beServerNew(int port);
void beServerStart(NovaServer* server);
void beServerRoute(NovaServer* server, const char* method, const char* path);

// Database (Fast Embedded SQLite / KV)
NovaDB beDbOpen(const char* path);
int beDbInsert(NovaDB* db, const char* table, const char* jsonRow);
const char* beDbFind(NovaDB* db, const char* table, const char* query);

// Auth
const char* beAuthHash(const char* password);
bool beAuthVerify(const char* password, const char* hash);
const char* beAuthToken(const char* user, const char* role);

// Cache & Store
void beCacheSet(const char* key, const char* val, int ttl);
const char* beCacheGet(const char* key);
void beStoreSave(const char* key, const char* jsonVal);
const char* beStoreLoad(const char* key);

// WebSockets & Real-Time
typedef struct {
    int port;
    int clientCount;
    bool isRunning;
} NovaWsServer;

NovaWsServer beWsServerNew(int port);
void beWsServerStart(NovaWsServer* server);
void beWsBroadcast(const char* event, const char* data);
void beWsSend(const char* clientId, const char* data);
void beWsJoinRoom(const char* room, const char* clientId);
void beWsEmitRoom(const char* room, const char* event, const char* data);

// Queue, Cron, Log, Session
void beQueueAdd(const char* jobName, const char* payload);
void beCronEvery(const char* interval, const char* taskName);
void beLogInfo(const char* msg);
const char* beSessionCreate(const char* user);

#endif // NOVA_BACKEND_H
