#ifndef SHA256_H
#define SHA256_H

#include <stdint.h>
#include <stddef.h>
#include <time.h>

#define SHA256_BLOCK_SIZE 64
#define SHA256_DIGEST_SIZE 32

typedef uint8_t BYTE;
typedef uint32_t WORD;

typedef struct {
    BYTE data[64];
    uint32_t datalen;
    uint64_t bitlen;
    WORD state[8];
} SHA256_CTX;

// ======== Các hàm cốt lõi SHA256 ========
void sha256_init(SHA256_CTX *ctx);
void sha256_update(SHA256_CTX *ctx, const BYTE *data, size_t len);
void sha256_final(SHA256_CTX *ctx, BYTE hash[]);

// ======== Hàm wrapper SHA256 đơn giản ========
void sha256(const BYTE *data, size_t len, BYTE digest[SHA256_DIGEST_SIZE]);

// ======== HMAC-SHA256 với timestamp ========
void hmac_sha256(
    const BYTE *key, size_t keylen,
    const BYTE *msg, size_t msglen,
    time_t timestamp,
    BYTE digest[SHA256_DIGEST_SIZE]
);

#endif