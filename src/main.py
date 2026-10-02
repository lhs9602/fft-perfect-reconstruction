import wave  # WAV 파일을 읽고 쓰는 표준 라이브러리
import dft  # 느린 DFT 와 겹침 없는 복원  # noqa: F401
import testvec as tv  # 복원한 WAV 를 원본과 비교하는 검사 도구  # noqa: F401
import math

INPUT_DIR = "data/input"  # 읽을 폴더 (프로젝트 폴더 기준)
OUTPUT_DIR = "data/output"  # 쓸 폴더 (프로젝트 폴더 기준)
WAV_NAME = "alarm.wav"  # 읽을 WAV 파일 이름
RESTORED_PREFIX = "복원_"  # 복원한 파일 이름 앞에 붙이는 말
INPUT_PATH = f"{INPUT_DIR}/{WAV_NAME}"  # 읽을 파일 경로
OUTPUT_PATH = f"{OUTPUT_DIR}/{RESTORED_PREFIX}{WAV_NAME}"  # 쓸 파일 경로. 있으면 덮어쓴다
SCALE = 32768  # 2^15. 16bit 정수를 이 값으로 나누면 -1 <= x < 1 의 float 이 된다


def read_wav(path):
    # with: 파일을 열고, 아래 블록이 끝나면 저절로 닫는다
    # "rb" = 읽기(read) + 바이너리(binary)
    with wave.open(path, "rb") as wav_file:
        channels = wav_file.getnchannels()  # 채널 수 (1 = 모노, 2 = 스테레오)
        width = wav_file.getsampwidth()  # 샘플 하나의 바이트 수 (2 = 16bit)
        rate = wav_file.getframerate()  # 샘플링 주파수 (1초에 샘플 몇 개)
        frames = wav_file.getnframes()  # 프레임 수. WAV 의 프레임 = 채널마다 샘플 하나씩. 모노면 샘플 수
        data = wav_file.readframes(frames)  # 샘플 전체를 bytes 로 읽는다

    # 여기부터는 with 블록 밖이다. 파일은 이미 닫혔고, 읽어 둔 값만 쓴다
    print("파일:", path)
    print("채널 수:", channels)
    print("샘플 폭:", width, "바이트")
    print("샘플링 주파수:", rate, "Hz")
    print("프레임 수:", frames)
    print("길이:", frames / rate, "초")  # 프레임 수 / 샘플링 주파수

    # 2 바이트씩 묶어 little-endian 부호 있는 16bit 정수로 바꾼다
    samples = []  # 샘플을 담을 리스트
    for i in range(0, len(data), 2):  # i = 0, 2, 4, ... (샘플 하나가 2 바이트)
        value = data[i] + data[i + 1] * 256  # 아래 바이트 + 위 바이트 * 256 (0 ~ 65535)
        if value >= 32768:  # 맨 위 비트가 1 이면 음수다
            value = value - 65536  # -32768 ~ -1 로 바꾼다
        samples.append(value / SCALE)  # -1 <= x < 1 의 float 으로 바꿔 붙인다
    return samples, channels, width, rate  # 샘플, 채널 수, 샘플 폭, 샘플링 주파수


def write_wav(path, samples, channels, width, rate):
    samples = [max(-32768, min(32767, round(sample * SCALE))) for sample in samples]  # float 을 16bit 정수로 되돌린다. 반올림하고 16bit 범위를 넘으면 자른다
    # 정수 하나를 width 바이트 little-endian 부호 있는 값으로 바꾸고,
    # b"".join(...) 으로 그 bytes 들을 하나로 이어 붙인다
    data = b"".join(sample.to_bytes(width, "little", signed=True) for sample in samples)
    # "wb" = 쓰기(write) + 바이너리. with 블록이 끝나면 파일이 닫힌다
    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(channels)  # 채널 수 (읽은 값)
        wav_file.setsampwidth(width)  # 샘플 폭 (읽은 값)
        wav_file.setframerate(rate)  # 샘플링 주파수 (읽은 값)
        wav_file.writeframes(data)  # 샘플을 쓰고 헤더의 프레임 수를 맞춘다


# 공식:
#     order[i] = i 의 아래 B 비트를 거꾸로 읽은 수
#     B = log2(N)
#     범위: i = 0 ~ N-1
#     예: N = 8 (B = 3) 이면 i = 3 (011) -> 110 = 6
#
# 기호:
#     N        : 전체 샘플 수. 2 의 거듭제곱
#     B        : 번호 하나를 적는 비트 수 (코드의 bit_count)
#     i        : 원래 번호
#     order[i] : i 의 비트 순서를 뒤집은 번호
def bit_reverse_order(N):
    # 0 ~ N-1 의 번호마다 비트를 뒤집은 번호를 차례로 담는다 (길이 8 이면 0, 4, 2, 6, 1, 5, 3, 7)
    order = []  # 결과 order[0] ~ order[N-1] 을 담을 리스트
    bit_count = 0  # 비트 수
    remaining = N  # N 을 2 로 나눠 가는 값
    while remaining > 1:  # 1 보다 큰 동안 반복한다
        remaining = remaining // 2  # 2 로 나눈다
        bit_count += 1  # 비트 수를 1 늘린다
    for i in range(N):  # 번호 i = 0 ~ N-1
        reversed_index = 0  # 뒤집은 번호
        value = i  # i 를 오른쪽으로 밀어 가는 값
        for _ in range(bit_count):  # 비트 수만큼 반복한다
            reversed_index = (reversed_index << 1) | (value & 1)  # 왼쪽으로 한 칸 밀고 value 의 맨 아래 비트를 붙인다
            value = value >> 1  # 오른쪽으로 한 칸 민다
        order.append(reversed_index)  # 뒤집은 번호를 order 에 붙인다
    return order


# 공식:
#     W[k] = cos(θ) - j*sin(θ)
#     θ = 2πk / N
#     범위: k = 0 ~ N/2 - 1
#
# 기호:
#     N    : 전체 샘플 수. 2 의 거듭제곱
#     k    : 회전 인자 표의 번호
#     W[k] : 회전 인자 (코드의 table[k])
#     j    : 허수 단위. j² = -1
def twiddle_table(N):
    # 회전 인자 표. 한 바퀴를 N 등분해 시계 방향으로 k 눈금 회전한 크기 1 인 복소수 (k = 0 ~ N/2 - 1) 를 차례로 담는다
    table = []  # 결과 table[0] ~ table[N/2 - 1] 을 담을 리스트
    for k in range(N // 2):  # k = 0 ~ N/2 - 1
        angle = (2 * math.pi * k) / N  # 번호 k 의 각도 θ (라디안)
        table.append(complex(math.cos(angle), -math.sin(angle)))  # W[k] 의 실수부 cos(θ), 허수부 -sin(θ) 를 복소수로 담아 table 에 붙인다
    return table


# 공식:
#     X[k]       = E[k] + W[k] * O[k]
#     X[k + N/2] = E[k] - W[k] * O[k]
#     범위: k = 0 ~ N/2 - 1
#     이 식을 길이 2, 4, 8, ..., N 의 묶음에 차례로 쓴다
#     묶음 하나 (길이 size) 에서는 N 대신 size, k 대신 j 로 쓴다
#     바꾸기 전: E[j] = X[first], O[j] = X[second], W[j] = table[j * (N // size)]
#     바꾼 뒤: X[first] = E[j] + W[j] * O[j], X[second] = E[j] - W[j] * O[j]
#     first = start + j, second = first + half
#     복소수 곱: (a, b) * (c, d) = (ac - bd, ad + bc)
#
# 기호:
#     N      : 전체 샘플 수. 2 의 거듭제곱
#     k      : 주파수 bin 번호
#     X[k]   : k번 주파수의 크기와 위상 정보를 담은 복소수. 반복 중에는 묶음마다의 중간 값을 담는다
#     E[k]   : 묶음에 든 샘플 중 짝수 자리 (0, 2, 4, ...) 의 샘플만으로 구한 절반 길이의 DFT
#     O[k]   : 묶음에 든 샘플 중 홀수 자리 (1, 3, 5, ...) 의 샘플만으로 구한 절반 길이의 DFT
#     W[k]   : 회전 인자
#     size   : 묶음 길이
#     half   : 묶음 길이의 절반
#     start  : 묶음의 시작 칸 번호
#     j      : 묶음 안의 짝 번호 (여기서는 허수 단위가 아니다)
#     first  : 첫째 칸 번호
#     second : 둘째 칸 번호
#     (a, b), (c, d), (e, f) : 실수부, 허수부 순서로 쓴 복소수
def fft(x):
    # radix-2 FFT. 비트 반전 순서로 늘어놓은 뒤 길이 2, 4, ..., N 의 묶음을 차례로 합친다
    N = len(x)  # 입력 길이. 2 의 거듭제곱이어야 한다
    order = bit_reverse_order(N)  # 비트 반전 순서
    table = twiddle_table(N)  # 회전 인자 표
    X = []  # 입력을 비트 반전 순서로 늘어놓을 새 리스트. 아래 반복에서 값이 바뀌어 결과가 된다. 입력 x 는 고치지 않는다
    for i in range(N):  # 칸 i = 0 ~ N-1
        value = x[order[i]]  # 입력에서 order[i] 번째 값을 꺼낸다
        X.append(complex(value))  # 복소수로 바꿔 X 에 붙인다
    size = 2  # 묶음 길이. 2, 4, 8, ..., N 으로 두 배씩 키운다
    while size <= N:  # 묶음 길이가 N 이하인 동안
        half = size // 2  # 묶음 길이의 절반. 짝이 되는 두 칸 사이의 거리
        for start in range(0, N, size):  # 묶음의 시작 칸 0, size, 2 * size, ...
            for j in range(half):  # 묶음 앞쪽 절반의 칸 start + j
                first = start + j  # 첫째 칸 번호
                second = first + half  # 둘째 칸 번호
                w = table[j * (N // size)]  # 회전 인자 (a, b)
                second_value = X[second]  # 둘째 칸 값 (c, d)
                first_value = X[first]  # 첫째 칸 값 (e, f)
                product_re = w.real * second_value.real - w.imag * second_value.imag  # 곱의 실수부 = ac - bd
                product_im = w.real * second_value.imag + w.imag * second_value.real  # 곱의 허수부 = ad + bc
                X[first] = complex(first_value.real + product_re, first_value.imag + product_im)  # 첫째 칸 = (e + 곱의 실수부, f + 곱의 허수부)
                X[second] = complex(first_value.real - product_re, first_value.imag - product_im)  # 둘째 칸 = (e - 곱의 실수부, f - 곱의 허수부)
        size *= 2  # 다음 묶음 길이
    return X


# 공식:
#     x[n] = conj(FFT(conj(X)))[n] / N
#     conj((a, b)) = (a, -b)
#
# 기호:
#     N      : 전체 샘플 수. 2 의 거듭제곱
#     n      : 되돌릴 샘플의 위치
#     X      : 주파수 bin N 개의 복소수
#     x[n]   : 되돌린 n번째 샘플값 (복소수)
#     FFT    : fft 함수
#     conj   : 허수부의 부호를 바꾸는 것
#     (a, b), (c, d) : 실수부, 허수부 순서로 쓴 복소수
def ifft(X):
    # 역 FFT. 허수부 부호를 바꿔 fft 를 하고, 다시 허수부 부호를 바꿔 N 으로 나눈다
    N = len(X)  # 입력 길이. 2 의 거듭제곱이어야 한다
    conjugated = []  # X 의 허수부 부호를 바꾼 리스트
    for k in range(N):  # bin k = 0 ~ N-1
        conjugated.append(complex(X[k].real, -X[k].imag))  # (a, b) -> (a, -b)
    Y = fft(conjugated)  # fft 결과. Y[n] = (c, d)
    x = []  # 결과 x[0] ~ x[N-1] 을 담을 리스트
    for n in range(N):  # 샘플 n = 0 ~ N-1
        x.append(complex(Y[n].real / N, -Y[n].imag / N))  # (c, d) -> (c / N, -d / N)
    return x


def restore_no_overlap(samples):
    # 겹침 없는 복원. 512 개씩 겹치지 않게 잘라 fft 뒤 ifft 로 되돌리고 이어 붙인다
    size = 512  # 블록 하나의 길이
    restored = []  # 되돌린 값을 이어 붙일 리스트
    for start in range(0, len(samples), size):  # 블록 시작 자리 0, 512, 1024, ...
        block = []  # 이번 블록 512 개를 담을 리스트
        for off in range(size):  # 블록 안의 번호 off = 0 ~ 511
            src = start + off  # 꺼낼 샘플 번호
            if src < len(samples):  # 입력 안이면
                block.append(samples[src])  # 그 샘플을 붙인다
            else:  # 입력이 끝난 뒤면
                block.append(0)  # 0 을 붙인다
        y = ifft(fft(block))  # 주파수 bin 512 개로 바꿨다가 다시 샘플 512 개로 되돌린다 (값은 복소수)
        for pos in range(size):  # 되돌린 값의 번호 pos = 0 ~ 511
            if start + pos < len(samples):  # 입력 안의 자리만
                restored.append(y[pos].real)  # 실수부를 붙인다
    return restored  # 복원한 float 리스트


# 공식:
#     w[i] = 0.5 - 0.5*cos(θ)
#     θ = 2πi / (N - 1)
#     W[r] = Σ w[i], i = r + q*R
#     범위: i = 0 ~ N-1, r = 0 ~ R-1, q = 0 ~ N/R - 1
#
# 기호:
#     N    : 윈도우 길이. 2 이상이고 R 의 배수
#     R    : 프레임 크기. 프레임마다 새로 넣는 샘플 수
#     i    : 윈도우 안에서의 번호
#     r    : 프레임 안에서의 위치
#     q    : 더할 차례. 코드에서는 idx 를 r 부터 R 씩 늘린다
#     w[i] : 윈도우의 i번째 값. 0 이상 1 이하의 실수 (코드의 window[i])
#     W[r] : 위치 r 의 윈도우 합 (코드의 sums[r])
def hanning_window(N, R):
    # 대칭형 Hanning 윈도우와 위치별 윈도우 합을 만든다
    window = []  # 윈도우 window[0] ~ window[N-1] 을 담을 리스트
    for i in range(N):  # 번호 i = 0 ~ N-1
        angle = (2 * math.pi * i) / (N - 1)  # 번호 i 의 각도 θ (라디안)
        window.append(0.5 - 0.5 * math.cos(angle))  # w[i] 를 window 에 붙인다
    sums = []  # 윈도우 합 sums[0] ~ sums[R-1] 을 담을 리스트
    for r in range(R):  # 위치 r = 0 ~ R-1
        total = 0  # 위치 r 의 합
        for idx in range(r, N, R):  # idx = r, r + R, r + 2*R, ...
            total += window[idx]  # w[idx] 를 더한다
        sums.append(total)  # W[r] 을 sums 에 붙인다
    return window, sums  # 윈도우, 위치별 윈도우 합


# 공식:
#     X[k] = FFT(v)[k]
#     v[i] = b[i] * w[i]
#     범위: i = 0 ~ N-1
#
# 기호:
#     N    : 버퍼와 윈도우의 길이
#     k    : 주파수 bin 번호
#     i    : 버퍼 안에서의 번호
#     b[i] : 버퍼의 i번째 값 (코드의 buffer[i])
#     w[i] : 윈도우의 i번째 값 (코드의 window[i])
#     v[i] : 윈도우를 곱한 값 (코드의 windowed[i])
#     X[k] : 이 프레임의 k번 주파수의 크기와 위상 정보를 담은 복소수
#     FFT  : fft 함수
def analyze(buffer, window):
    # 프레임 하나의 분석. 버퍼에 윈도우를 곱하고 fft 를 한다
    N = len(buffer)  # 버퍼 길이
    windowed = []  # 윈도우를 곱한 값 windowed[0] ~ windowed[N-1] 을 담을 리스트
    for i in range(N):  # 번호 i = 0 ~ N-1
        windowed.append(buffer[i] * window[i])  # b[i] * w[i] 를 windowed 에 붙인다
    return fft(windowed)  # 스펙트럼 X[k]


# 공식:
#     M = ceil(L / R) + N/R - 1
#     b[i] = x[(m + 1)*R - N + i]
#     X = FFT(v), v[i] = b[i] * w[i]
#     y[n] = y[n] + IFFT(X)[i].real, n = (m + 1)*R - N + i, 0 <= n < L 일 때만
#     xr[n] = y[n] / W[n % R]
#     범위: m = 0 ~ M-1, i = 0 ~ N-1, n = 0 ~ L-1
#
# 기호:
#     N     : 버퍼와 FFT 의 길이 (코드의 buf_len, 512)
#     R     : 프레임 크기. 프레임마다 새로 넣는 샘플 수 (코드의 step, 16)
#     L     : 입력 샘플 수 (코드의 total)
#     M     : 프레임 수 (코드의 frames)
#     m     : 프레임 번호 (코드의 frame)
#     i     : 버퍼 안에서의 번호. 0 이 가장 오래된 샘플 (코드의 pos, slot)
#     n     : 입력 전체에서의 샘플 번호 (코드의 src, dst, idx)
#     x[n]  : n번째 입력 샘플값 (코드의 samples[n]). n 이 0 보다 작거나 L 이상이면 0 으로 본다
#     b[i]  : 프레임 m 의 버퍼 (코드의 buf[i])
#     w[i]  : 윈도우의 i번째 값 (코드의 window[i])
#     v[i]  : 윈도우를 곱한 값
#     X     : 프레임 m 의 스펙트럼
#     IFFT(X) : 코드의 windowed
#     y[n]  : 겹쳐 더한 값 (코드의 added[n])
#     W[r]  : 위치 r 의 윈도우 합 (코드의 sums[r])
#     xr[n] : 되돌린 n번째 샘플값 (코드의 restored[n])
#     n % R : n 을 R 로 나눈 나머지
#     ceil  : 올림
#     FFT, IFFT : fft 함수, ifft 함수
def restore_overlap(samples):
    # 겹침 있는 복원. 16 개씩 밀어 넣은 512 칸 버퍼에 윈도우를 곱해 fft 하고, ifft 한 값을 겹쳐 더한 뒤 윈도우 합으로 나눈다
    buf_len = 512  # 버퍼와 FFT 의 길이
    step = 16  # 프레임마다 새로 넣는 샘플 수
    total = len(samples)  # 입력 샘플 수
    window, sums = hanning_window(buf_len, step)  # 윈도우, 위치별 윈도우 합
    frames = (total + step - 1) // step + buf_len // step - 1  # 프레임 수. 입력을 다 넣는 올림(total / step) + 마지막 샘플이 버퍼를 빠져나가는 buf_len / step - 1. 샘플마다 윈도우의 32 자리를 다 지나야 복원된다
    buf = [0] * buf_len  # 버퍼. 1.5 처럼 0 으로 시작하고 프레임마다 뒤에 step 개씩 들어온다. 처음 31 프레임은 덜 찬 채로 fft 한다
    added = [0] * total  # 겹쳐 더한 값. 0 으로 시작한다
    for frame in range(frames):  # 프레임 0 ~ frames-1
        for pos in range(buf_len - step):  # 버퍼 번호 pos = 0 ~ buf_len-step-1
            buf[pos] = buf[pos + step]  # 버퍼의 값을 앞으로 step 칸 당긴다
        for off in range(step):  # 새로 넣는 칸의 차례 off = 0 ~ step-1
            src = frame * step + off  # 가져올 샘플 번호
            if src < total:  # 입력 안이면
                buf[buf_len - step + off] = samples[src]  # 버퍼의 뒤 step 칸에 새 샘플을 넣는다
            else:  # 입력이 끝난 뒤면
                buf[buf_len - step + off] = 0  # 0 을 넣는다
        windowed = ifft(analyze(buf, window))  # 분석하고 합성. 버퍼에 윈도우를 곱한 값 buf_len 개가 나온다 (복소수)
        first = (frame + 1) * step - buf_len  # 버퍼의 0 번 칸에 든 샘플의 번호. 맨 뒤 칸이 (frame + 1) * step - 1 번이고 그보다 buf_len - 1 앞이다. 처음 31 프레임은 음수다 (아직 0 인 칸)
        for slot in range(buf_len):  # 버퍼 번호 slot = 0 ~ buf_len-1
            dst = first + slot  # 버퍼의 slot 번 칸에 든 샘플의 번호. 더할 자리
            if 0 <= dst < total:  # 입력에 있는 번호면 (음수와 total 이상은 0 을 채운 칸이라 버린다)
                added[dst] += windowed[slot].real  # 실수부를 그 샘플의 자리에 더한다
    restored = []  # 결과를 담을 리스트
    for idx in range(total):  # 샘플 0 ~ total-1
        restored.append(added[idx] / sums[idx % step])  # 겹쳐 더한 값을 위치 idx % step 의 윈도우 합으로 나눠 붙인다
    return restored  # 복원한 float 리스트


def main():
    # 함수가 값을 여러 개 돌려주면 받는 쪽도 같은 순서로 나눠 받는다
    samples, channels, width, rate = read_wav(INPUT_PATH)

    # 겹침 없는 DFT 복원. 쓰려면 아래 세 줄의 주석을 풀고 맨 아래 복원 세 줄을 주석 처리한다
    # restored = dft.restore_no_overlap(samples)  # 겹침 없는 복원
    # write_wav(OUTPUT_PATH, restored, channels, width, rate)  # 복원한 샘플을 읽은 헤더 값으로 쓴다
    # tv.compare_wav(INPUT_PATH, OUTPUT_PATH)  # 원본과 비교해 판정과 복원율을 출력한다

    # 겹침 없는 FFT 복원. 쓰려면 아래 세 줄의 주석을 풀고 맨 아래 복원 세 줄을 주석 처리한다
    # restored = restore_no_overlap(samples)  # 겹침 없는 복원
    # write_wav(OUTPUT_PATH, restored, channels, width, rate)  # 복원한 샘플을 읽은 헤더 값으로 쓴다
    # tv.compare_wav(INPUT_PATH, OUTPUT_PATH)  # 원본과 비교해 판정과 복원율을 출력한다

    # 겹침 있는 FFT 복원
    restored = restore_overlap(samples)  # 겹침 있는 복원
    write_wav(OUTPUT_PATH, restored, channels, width, rate)  # 복원한 샘플을 읽은 헤더 값으로 쓴다
    tv.compare_wav(INPUT_PATH, OUTPUT_PATH)  # 원본과 비교해 판정과 복원율을 출력한다


# 실행 (프로젝트 폴더에서):
#     .venv\Scripts\python.exe src\main.py
# 시험:
#     .venv\Scripts\python.exe -m pytest -v
if __name__ == "__main__":  # 직접 실행할 때만 main() 을 부른다 (import 될 때는 부르지 않는다)
    main()
