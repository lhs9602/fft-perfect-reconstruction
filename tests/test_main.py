"""src/main.py 의 시험.

실행: 프로젝트 폴더에서 python -m pytest -v
"""

import math

import main
import testvec as tv


def test_main_exists():
    """main.py 가 불러와지고 main 함수가 있는지 본다."""
    assert callable(main.main)


# ---------------------------------------------------------------------------
# 시험은 여기에 쓴다. DFT 시험은 tests/test_dft.py 에 있다
# ---------------------------------------------------------------------------


# radix-2 FFT
def test_bit_reverse_order():
    assert tv.compare("비트 반전, 길이 8", main.bit_reverse_order(8), [0, 4, 2, 6, 1, 5, 3, 7])
    order = main.bit_reverse_order(512)
    assert len(order) == 512  # 번호 512 개
    assert tv.compare("비트 반전, 길이 512 의 1, 2, 3, 4, 255 번", [order[i] for i in (1, 2, 3, 4, 255)], [256, 128, 384, 64, 510])


def test_twiddle_table():
    table = main.twiddle_table(512)
    assert len(table) == 256  # k = 0 ~ 255
    expected = [complex(1, 0), complex(math.sqrt(0.5), -math.sqrt(0.5)), complex(0, -1)]  # W^0 = 1, W^64 = 0.7071 - 0.7071j, W^128 = -j
    assert tv.compare("회전 인자 표 0, 64, 128 번", [table[k] for k in (0, 64, 128)], expected)


def test_fft_small():
    assert tv.check_function(main.fft, tv.FFT_CASES_SMALL)  # 길이 8 한 개. 이것부터 맞춘다


def test_fft():
    assert tv.check_function(main.fft, tv.FFT_CASES)  # 길이 512 다섯 개


# IFFT
def test_ifft():
    assert tv.check_function(main.ifft, tv.IFFT_CASES)  # 길이 512 다섯 개


def test_fft_ifft_roundtrip():
    x = tv.get_case("fft/speechlike")["input"]  # 길이 512 입력 하나
    assert tv.compare("fft -> ifft", main.ifft(main.fft(x)), x)  # FFT 뒤 IFFT 를 하면 입력으로 돌아온다


# 겹침 없는 복원
def test_restore_no_overlap():
    x = tv.get_case("fft/speechlike")["input"]  # 길이 512 입력 하나
    x = list(x) + list(x[:300])  # 길이 812. 마지막 블록이 512 개보다 짧다
    assert tv.compare("겹침 없는 복원, 길이 812", main.restore_no_overlap(x), x)  # 입력으로 돌아온다


def test_restore_no_overlap_wav(tmp_path):
    input_path = f"{main.INPUT_DIR}/sine_1k.wav"  # 읽을 파일
    output_path = str(tmp_path / "sine_1k.wav")  # 쓸 파일. pytest 가 만들어 주는 임시 폴더에 쓴다
    samples, channels, width, rate = main.read_wav(input_path)
    restored = main.restore_no_overlap(samples)
    main.write_wav(output_path, restored, channels, width, rate)
    result = tv.compare_wav(input_path, output_path)  # 원본과 복원을 비교한다
    assert result["verdict"] == "완전 복원"  # 샘플이 전부 같다


# Hanning 윈도우
def test_hanning_window():
    window, sums = main.hanning_window(512, 16)
    assert tv.check_window(window)  # 512 개를 기대값과 비교한다
    assert len(sums) == 16  # 위치 0 ~ 15
    expected = [15.968832743823, 15.968700335684, 15.968700335684, 15.968832743823]
    assert tv.compare("윈도우 합 0, 7, 8, 15 번", [sums[r] for r in (0, 7, 8, 15)], expected, abs_tol=1e-9)


def test_hanning_window_small():
    window, sums = main.hanning_window(8, 4)
    expected = [0, 0.188255099071, 0.611260466978, 0.950484433951, 0.950484433951, 0.611260466978, 0.188255099071, 0]
    assert tv.compare("Hanning 윈도우, 길이 8", window, expected, abs_tol=1e-9)  # 길이가 달라도 양 끝이 0 이다
    expected = [0.950484433951, 0.799515566049, 0.799515566049, 0.950484433951]
    assert tv.compare("윈도우 합, 길이 8 간격 4", sums, expected, abs_tol=1e-9)  # 0 + 4, 1 + 5, 2 + 6, 3 + 7 번의 합


# 분석
def test_analyze():
    assert tv.check_function(lambda buffer: main.analyze(buffer, tv.WINDOW_512), tv.ANALYSIS_CASES)  # 길이 512 세 개
    assert tv.compare("분석, 좌우가 다른 윈도우", main.analyze([1, 2, 3, 4], [1, 0, 0, 0]), [1, 1, 1, 1])  # 0 번만 남는다


# 겹침 있는 복원
def test_restore_overlap():
    x = tv.get_case("fft/speechlike")["input"]  # 길이 512 입력 하나
    x = list(x) + list(x[:300])  # 길이 812. 16 의 배수가 아니다
    assert tv.compare("겹침 있는 복원, 길이 812", main.restore_overlap(x), x, abs_tol=1e-9, rel_tol=0.0)  # 입력으로 돌아온다


def test_restore_overlap_frames(monkeypatch):
    buffers = []  # 프레임마다 분석에 들어간 버퍼를 모을 리스트
    real_analyze = main.analyze  # 원래 analyze

    def spy(buffer, window):
        buffers.append(list(buffer))  # 버퍼를 복사해 둔다
        return real_analyze(buffer, window)  # 원래 analyze 를 부른다

    monkeypatch.setattr(main, "analyze", spy)  # 이 시험 동안만 analyze 를 spy 로 바꾼다
    main.restore_overlap(list(range(600)))  # x[n] = n, 길이 600
    assert len(buffers) == 69  # 프레임 수. 600 / 16 의 올림 38 에 31 을 더한다
    assert all(len(buffer) == 512 for buffer in buffers)  # 버퍼 길이는 늘 512
    expected = {0: [0, 0, 0, 15], 1: [0, 15, 16, 31], 31: [0, 495, 496, 511], 32: [16, 511, 512, 527], 33: [32, 527, 528, 543]}
    for m in expected:  # 프레임 0, 1, 31, 32, 33 의 버퍼 0, 495, 496, 511 번
        assert [buffers[m][i] for i in (0, 495, 496, 511)] == expected[m]


def test_restore_overlap_before_division(monkeypatch):
    window, sums = main.hanning_window(512, 16)  # 윈도우, 위치별 윈도우 합
    monkeypatch.setattr(main, "hanning_window", lambda N, R: (window, [1.0] * R))  # 이 시험 동안만 나누는 값을 1 로 바꾼다
    y = main.restore_overlap([1.0] * 100)  # 입력이 모두 1 이면 나누기 전의 값은 위치별 윈도우 합이다
    assert tv.compare("나누기 전의 값, 길이 100", y, [sums[n % 16] for n in range(100)], abs_tol=1e-9, rel_tol=0.0)


def test_restore_overlap_uses_spectrum(monkeypatch):
    real_analyze = main.analyze  # 원래 analyze

    def doubled(buffer, window):
        return [complex(value.real * 2, value.imag * 2) for value in real_analyze(buffer, window)]  # 스펙트럼을 2 배 한다

    monkeypatch.setattr(main, "analyze", doubled)  # 이 시험 동안만 analyze 를 doubled 로 바꾼다
    x = [100, -200, 300, 50] * 10  # 길이 40
    assert tv.compare("스펙트럼을 2 배 하면 복원도 2 배, 길이 40", main.restore_overlap(x), [2 * value for value in x])


def test_restore_overlap_wav(tmp_path):
    input_path = f"{main.INPUT_DIR}/sine_1k.wav"  # 읽을 파일
    output_path = str(tmp_path / "sine_1k.wav")  # 쓸 파일. pytest 가 만들어 주는 임시 폴더에 쓴다
    samples, channels, width, rate = main.read_wav(input_path)
    restored = main.restore_overlap(samples)
    main.write_wav(output_path, restored, channels, width, rate)
    result = tv.compare_wav(input_path, output_path)  # 원본과 복원을 비교한다
    assert result["verdict"] == "완전 복원"  # 샘플이 전부 같다
