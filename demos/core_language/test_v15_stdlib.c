// ============================================================
// Automatic Nova -> C Generated Source
// Target: windows | Optimized Native
// ============================================================
#include "nova_np.h"
#include "nova_runtime.h"
#include <math.h>
#undef max
#undef min


int main(int argc, char** argv) {
    srand((unsigned int)time(NULL));
    printf("==================================================\n");
    printf("  NOVA V1.5 STANDARD LIBRARY TEST SUITE\n");
    printf("==================================================\n");
    printf("=== 1. MATH MODULE ===\n");
    // import math
    printf("math.pi: "); printf("%g\n", (double)3.141592653589793);
    printf("math.e: "); printf("%g\n", (double)2.718281828459045);
    printf("math.tau: "); printf("%g\n", (double)6.283185307179586);
    printf("math.phi: "); printf("%g\n", (double)1.618033988749895);
    printf("math.root(16): "); printf("%g\n", (double)sqrt((double)(16)));
    printf("math.power(2, 3): "); printf("%g\n", (double)pow((double)(2), (double)(3)));
    printf("math.abs(-42): "); printf("%g\n", (double)fabs((double)(-42)));
    printf("math.floor(3.9): "); printf("%g\n", (double)floor((double)(3.9f)));
    printf("math.ceil(3.1): "); printf("%g\n", (double)ceil((double)(3.1f)));
    printf("math.round(3.6): "); printf("%g\n", (double)round((double)(3.6f)));
    printf("math.sin(math.pi / 2): "); printf("%g\n", (double)sin((double)((3.141592653589793 / 2))));
    printf("math.log10(100): "); printf("%g\n", (double)log10((double)(100)));
    printf("math.gcd(24, 36): "); printf("%lld\n", (long long)12);
    printf("math.lcm(12, 18): "); printf("%lld\n", (long long)12);
    printf("math.fact(5): "); printf("%g\n", (double)0.0f);
    printf("math.isEven(10): "); printf("%g\n", (double)0.0f);
    printf("math.isOdd(11): "); printf("%g\n", (double)0.0f);
    printf("math.isPrime(17): "); printf("%g\n", (double)0.0f);
    printf("math.prime(5): "); printf("%g\n", (double)0.0f);
    printf("math.clamp(15, 0, 10): "); printf("%lld\n", (long long)12);
    printf("math.lerp(0, 100, 0.5): "); printf("%g\n", (double)0.0f);
    printf("math.hypot(3, 4): "); printf("%g\n", (double)5.0f);
    printf("math.range(1, 5): "); printf("[1, 2, 3, 4, 5]\n");
    printf("=== 2. STRING MODULE ===\n");
    // import string
    printf("string.digits: "); printf("0123456789\n");
    printf("string.upper('hello'): "); printf("string_upper_result\n");
    printf("string.lower('NOVA'): "); printf("string_lower_result\n");
    printf("string.title('hello world'): "); printf("string_title_result\n");
    printf("string.cap('nova'): "); printf("string_cap_result\n");
    printf("string.trim('  clean  '): "); printf("string_trim_result\n");
    printf("string.has('banana', 'nan'): "); printf("%s\n", (1) ? "true" : "false");
    printf("string.starts('python', 'py'): "); printf("%s\n", (long long)0);
    printf("string.ends('nova.lang', 'lang'): "); printf("%s\n", (long long)0);
    printf("string.padL('42', 5, '0'): "); printf("%s\n", (long long)0);
    printf("string.padR('42', 5, '-'): "); printf("%s\n", (long long)0);
    printf("string.repeat('abc', 3): "); printf("%s\n", (long long)0);
    printf("string.reverse('nova'): "); printf("%s\n", (long long)0);
    printf("string.wordC('The quick brown fox'): "); printf("%s\n", (long long)0);
    printf("string.codeAt('A', 0): "); printf("%s\n", (long long)0);
    printf("string.fromCode(65): "); printf("%s\n", (long long)0);
    printf("=== 3. LIST MODULE ===\n");
    // import list
    void* l = (void*)((long long)0);
    printf("list.range(1, 6): "); printf("%s\n", l);
    printf("list.sum(l): "); printf("%lld\n", (long long)26);
    printf("list.avg(l): "); printf("%g\n", (double)2.5f);
    printf("list.max(l): "); printf("%s\n", (long long)0);
    printf("list.min(l): "); printf("%s\n", (long long)0);
    printf("list.prod([2, 3, 4]): "); printf("%s\n", (long long)0);
    printf("list.unique([1, 2, 2, 3, 3, 3]): "); printf("%s\n", (long long)0);
    printf("list.freq([1, 2, 2, 3]): "); printf("%s\n", (long long)0);
    printf("list.flat([[1, 2], [3, 4], 5]): "); printf("%s\n", (long long)0);
    printf("list.chunk([1, 2, 3, 4, 5], 2): "); printf("%s\n", (long long)0);
    printf("list.window([1, 2, 3, 4], 2): "); printf("%s\n", (long long)0);
    printf("list.dsorted([3, 1, 4, 1, 5]): "); printf("%s\n", (long long)0);
    printf("list.hasAll([1, 2, 3], [1, 2]): "); printf("%s\n", (1) ? "true" : "false");
    printf("=== 4. SET MODULE ===\n");
    // import set
    numpyarray s1 = npArray((float[]){1.0f, 2.0f, 3.0f, 4.0f}, 4);
    numpyarray s2 = npArray((float[]){3.0f, 4.0f, 5.0f, 6.0f}, 4);
    printf("set.U(s1, s2): "); printf("%s\n", (long long)0);
    printf("set.N(s1, s2): "); printf("%s\n", (long long)0);
    printf("set.diff(s1, s2): "); printf("%s\n", (long long)0);
    printf("set.isSub(%s, s1):\n", 1, 2); printf("%s\n", (1) ? "true" : "false");
    printf("set.isDisjoint(s1, %s):\n", 99, 100); printf("%s\n", (1) ? "true" : "false");
    printf("set.toList(s1): "); printf("%s\n", (long long)0);
    printf("set.cart(%s, %s):\n", 1, 2, 'a', 'b'); printf("%s\n", (long long)0);
    printf("=== 5. FILE & OS MODULE ===\n");
    // import file
    printf("Current pwd: "); printf("file_pwd_result\n");
    const char* test_file = "nova_test_file.txt";
    (long long)0;
    printf("file.exists(test_file): "); printf("%s\n", (1) ? "true" : "false");
    printf("file.readA(test_file):\n");
    printf("%s\n", (long long)0);
    printf("file.lineC(test_file): "); printf("%s\n", (long long)0);
    printf("file.hasText(test_file, 'Nova'): "); printf("%s\n", (long long)0);
    printf("Fluent open().read(): "); printf("Nova\n");
    (long long)0;
    printf("After remove exists: "); printf("%s\n", (1) ? "true" : "false");
    printf("=== 6. RANDOM MODULE ===\n");
    // import random
    (long long)0;
    printf("random.int(1, 100): "); printf("%s\n", (long long)0);
    printf("random.bool(): "); printf("%s\n", (1) ? "true" : "false");
    printf("random.pick(['apple', 'banana', 'cherry']): "); printf("%s\n", (long long)0);
    printf("random.pickN([10, 20, 30, 40, 50], 3): "); printf("%s\n", (long long)0);
    printf("random.str(8): "); printf("random_str_result\n");
    printf("random.otp(6): "); printf("random_otp_result\n");
    printf("random.pass(10): "); printf("random_pass_result\n");
    printf("random.dice(): "); printf("%s\n", (long long)0);
    printf("random.coin(): "); printf("%s\n", (long long)0);
    printf("random.card(): "); printf("random_card_result\n");
    printf("random.uuid(): "); printf("random_uuid_result\n");
    printf("=== 7. TIME MODULE ===\n");
    // import time
    printf("time.date(): "); printf("time_date_result\n");
    printf("time.now(): "); printf("time_now_result\n");
    printf("time.year(): "); printf("%lld\n", (long long)26);
    printf("time.isLeap(2024): "); printf("%s\n", (1) ? "true" : "false");
    printf("time.isLeap(2025): "); printf("%s\n", (1) ? "true" : "false");
    const char* t_now = "time_now_result";
    printf("time.addDay(t_now, 5): "); printf("%s\n", (long long)0);
    printf("time.subYear(t_now, 1): "); printf("%s\n", (long long)0);
    printf("time.format(t_now, 'YYYY/MM/DD'): "); printf("time_format_result\n");
    void* t_start = (void*)((long long)0);
    (long long)0;
    printf("time.elapsed(t_start) > 0: "); printf("%lld\n", (long long)((long long)0 > 0));
    printf("time.age('2000-01-01') >= 24: "); printf("%lld\n", (long long)(26 >= 24));
    printf("=== 8. JSON MODULE ===\n");
    // import json
    long long data = 0;
    const char* json_str = "json_text_result";
    printf("json.text(data): "); printf("%s\n", json_str);
    void* parsed = (void*)((long long)0);
    printf("json.map parsed['name']: "); printf("Nova\n");
    printf("json.getPath config.mode: "); printf("%s\n", (long long)0);
    (long long)0;
    printf("After setPath config.threads: "); printf("%s\n", (long long)0);
    printf("json.flat(data): "); printf("%s\n", (long long)0);
    printf("json.isValid(json_str): "); printf("%s\n", (1) ? "true" : "false");
    printf("json.isValid('invalid json'): "); printf("%s\n", (1) ? "true" : "false");
    long long d1 = 0;
    long long d2 = 0;
    void* diff_obj = (void*)((long long)0);
    printf("json.diff(d1, d2): "); printf("%s\n", diff_obj);
    void* patched = (void*)((long long)0);
    printf("json.patch(d1, diff): "); printf("%s\n", patched);
    printf("==================================================\n");
    printf("  ALL NOVA V1.5 STANDARD LIBRARY TESTS PASSED!\n");
    printf("==================================================\n");
    return 0;
}
