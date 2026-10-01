# 느린 DFT, 역 DFT 와 겹침 없는 복원
import math  # cos, sin, pi 를 쓴다


# 공식:
#     X[k] = Σ x[n] * (cos(θ) - j*sin(θ))
#     θ = 2πkn / N
#     합산 범위: n = 0 ~ N-1
#     복소수 곱: (a + j*b) * (c + j*d) = (ac - bd) + j*(ad + bc)
#
# 기호:
#     N    : 전체 샘플 수
#     n    : 입력 샘플의 위치
#     k    : 계산할 주파수 bin 번호
#     x[n] : n번째 입력 샘플값
#     X[k] : k번 주파수의 크기와 위상 정보를 담은 복소수
#     j    : 허수 단위. j² = -1
#     a, b : x[n] 의 실수부와 허수부 (실수 입력이면 b = 0)
#     c, d : cos(θ) 와 -sin(θ) (코드의 w_re, w_im)
def dft(x):
    # 느린 DFT. x[n] 에 회전 인자를 곱해 모두 더한다
    N = len(x)  # 입력 길이
    X = []  # 결과 X[0] ~ X[N-1] 을 담을 리스트
    for k in range(N):  # 바깥 반복: 주파수 bin k = 0 ~ N-1
        total_re = 0  # X[k] 의 실수부 합
        total_im = 0  # X[k] 의 허수부 합
        for n in range(N):  # 안쪽 반복: 샘플 번호 n = 0 ~ N-1
            angle = (2 * math.pi * k * n) / N  # bin k, 샘플 n 의 각도 θ (라디안)
            w_re = math.cos(angle)  # 회전 인자의 실수부 c = cos(θ)
            w_im = -math.sin(angle)  # 회전 인자의 허수부 d = -sin(θ)
            total_re += x[n].real * w_re - x[n].imag * w_im  # 곱의 실수부 ac - bd 를 더한다
            total_im += x[n].real * w_im + x[n].imag * w_re  # 곱의 허수부 ad + bc 를 더한다
        X.append(complex(total_re, total_im))  # 두 합을 복소수 하나에 담아 X 에 붙인다
    return X


# 공식:
#     x[n] = (1 / N) * Σ X[k] * (cos(θ) + j*sin(θ))
#     θ = 2πkn / N
#     합산 범위: k = 0 ~ N-1
#     복소수 곱: (a + j*b) * (c + j*d) = (ac - bd) + j*(ad + bc)
#
# 기호:
#     N    : 전체 샘플 수
#     n    : 되돌릴 샘플의 위치
#     k    : 주파수 bin 번호
#     x[n] : 되돌린 n번째 샘플값 (복소수)
#     X[k] : k번 주파수의 크기와 위상 정보를 담은 복소수
#     j    : 허수 단위. j² = -1
#     a, b : X[k] 의 실수부와 허수부
#     c, d : cos(θ) 와 sin(θ) (코드의 w_re, w_im)
def idft(X):
    # 느린 역 DFT. X[k] 에 회전 인자를 곱해 모두 더하고 N 으로 나눈다
    N = len(X)  # 입력 길이
    x = []  # 결과 x[0] ~ x[N-1] 을 담을 리스트
    for n in range(N):  # 바깥 반복: 샘플 번호 n = 0 ~ N-1
        total_re = 0  # x[n] 의 실수부 합
        total_im = 0  # x[n] 의 허수부 합
        for k in range(N):  # 안쪽 반복: 주파수 bin k = 0 ~ N-1
            angle = (2 * math.pi * k * n) / N  # bin k, 샘플 n 의 각도 θ (라디안)
            w_re = math.cos(angle)  # 회전 인자의 실수부 c = cos(θ)
            w_im = math.sin(angle)  # 회전 인자의 허수부 d = sin(θ)
            total_re += X[k].real * w_re - X[k].imag * w_im  # 곱의 실수부 ac - bd 를 더한다
            total_im += X[k].real * w_im + X[k].imag * w_re  # 곱의 허수부 ad + bc 를 더한다
        x.append(complex(total_re / N, total_im / N))  # 두 합을 각각 N 으로 나눠 복소수 하나에 담아 x 에 붙인다
    return x


def restore_no_overlap(samples):
    # 겹침 없는 복원. 512 개씩 겹치지 않게 잘라 dft 뒤 idft 로 되돌리고 이어 붙인다
    size = 512  # 블록 하나의 길이
    restored = []  # 되돌린 값을 이어 붙일 리스트
    for start in range(0, len(samples), size):  # 블록 시작 자리 0, 512, 1024, ...
        block = samples[start:start + size]  # 이번 블록. 마지막 블록은 512 개보다 짧을 수 있다
        block = block + [0] * (size - len(block))  # 모자란 만큼 0 을 채워 512 개로 맞춘다
        y = idft(dft(block))  # 주파수 bin 512 개로 바꿨다가 다시 샘플 512 개로 되돌린다 (값은 복소수)
        restored.extend(value.real for value in y)  # 실수부만 이어 붙인다
    restored = restored[:len(samples)]  # 0 을 채운 만큼 길어진 끝을 잘라 입력 길이로 맞춘다
    return restored  # 복원한 float 리스트


# 이전 dft 코드
# def dft(x):
#     # 느린 DFT. 칸 k 마다 x[n] 에 cos, -sin 을 곱해 모두 더한다
#     N = len(x)  # 입력 길이. 칸의 수도 N 개다
#     X = []  # 결과 X[0] ~ X[N-1] 을 담을 리스트
#     for k in range(N):  # 칸 k 하나마다 X[k] 하나를 만든다
#         total_re = 0  # 칸 k 의 실수부 합
#         total_im = 0  # 칸 k 의 허수부 합
#         for n in range(N):  # 샘플 n 하나마다 항 하나를 더한다
#             angle = (2 * math.pi * k * n) / N  # 칸 k, 샘플 n 의 각도 (라디안)
#             horizontal_len = x[n] * math.cos(angle)  # x[n] 에 cos 을 곱한 값 (가로)
#             vertical_len = -x[n] * math.sin(angle)  # x[n] 에 sin 을 곱하고 부호를 바꾼 값 (세로)
#             total_re += horizontal_len  # 가로는 실수부 합에 더한다
#             total_im += vertical_len  # 세로는 허수부 합에 더한다
#         X.append(complex(total_re, total_im))  # 두 합을 복소수 하나에 담아 X 에 붙인다
#     return X  # 칸 N 개 (X[0] ~ X[N-1])
