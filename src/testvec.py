"""테스트 벡터 검사 함수.

여기에는 값을 비교하는 코드만 있다. FFT, IFFT, 윈도우를 직접 구현한 코드는 없다.
입력과 기대값은 testvec_data.py 에 따로 있다.

복원율 비교(2번)는 검증용으로 numpy 를 쓴다. 밀림을 찾을 때 numpy 의 FFT 를 부른다.
WAV 비교는 먼저 파일 전체를 비교하고(filecmp), 다를 때만 샘플을 비교한다.

쓰는 법:
    import testvec as tv

    tv.check_function(내가_만든_fft, tv.FFT_CASES)      # 함수를 통째로 검사
    tv.check_window(내가_만든_윈도우)                   # 윈도우 512개 검사
    tv.compare_wav("원본.wav", "복원.wav")              # WAV 두 개 비교, 복원율(%)
"""

import array
import filecmp
import math
import os
import sys
import traceback
import wave

import numpy as np

import testvec_data as data
from testvec_data import (
    N,
    SAMPLE_MIN,
    SAMPLE_MAX,
    WINDOW_512,
    FFT_CASES,
    FFT_CASES_SMALL,
    IFFT_CASES,
    WINDOWED_CASES,
    ANALYSIS_CASES,
)

# 기본 허용 오차. 차이가 (abs_tol + rel_tol x |기대값|) 이하이면 같다고 본다
DEFAULT_ABS_TOL = 1e-5
DEFAULT_REL_TOL = 1e-9

# 다른 자리를 몇 개까지 보여 줄지
DEFAULT_MAX_SHOW = 10

# 밀림을 찾을 때 살펴볼 후보의 수
SHIFT_CANDIDATE_COUNT = 50

# 판정에 쓰는 기준 (%)
NEARLY_SAME_PERCENT = 99.9      # 파형 유사도가 이 이상이면 거의 같다고 본다
SPECTRUM_SAME_PERCENT = 95.0    # 스펙트럼 유사도가 이 이상이면 크기는 같다고 본다
SPECTRUM_FRAME = 512            # 스펙트럼 유사도를 잴 때 자르는 길이
WAVEFORM_DIFFERENT_PERCENT = 90.0   # 파형 유사도가 이 미만이면 파형이 다르다고 본다
PARTLY_PERCENT = 50.0           # 겹친 구간의 일치율이 이 이상이면 일부는 복원되었다고 본다
GAIN_TOLERANCE = 0.001          # 크기 비가 1 에서 이보다 더 벗어나면 크기가 다르다고 본다


# ---------------------------------------------------------------------------
# 1. 테스트 벡터와 비교
# ---------------------------------------------------------------------------

def compare(name, actual, expected,
            abs_tol=DEFAULT_ABS_TOL, rel_tol=DEFAULT_REL_TOL, max_show=DEFAULT_MAX_SHOW):
    """결과(actual)와 기대값(expected)을 자리마다 비교한다.

    모두 같으면 True, 하나라도 다르면 False 를 돌려준다.
    실수와 복소수를 모두 받는다. 리스트, 튜플, numpy 배열을 받는다.
    """
    # 1. 결과를 리스트로 바꾼다
    if actual is None:
        print("[실패] %s : 결과가 None 이다. 함수가 return 으로 값을 돌려주는지 확인한다." % name)
        return False
    try:
        actual_list = list(actual)
    except TypeError:
        print("[실패] %s : 결과가 리스트가 아니다. 받은 값: %r" % (name, actual))
        return False
    expected_list = list(expected)

    # 2. 길이를 비교한다
    n = len(expected_list)
    if len(actual_list) != n:
        print("[실패] %s : 길이가 다르다. 기대 %d개, 실제 %d개" % (name, n, len(actual_list)))
        if len(actual_list) in (n // 2, n // 2 + 1):
            print("    힌트: 절반만 돌려주고 있다. 이 벡터는 %d개 전부를 기대한다." % n)
        return False

    # 3. 값을 복소수로 통일한다
    actual_c = []
    for index in range(n):
        try:
            actual_c.append(complex(actual_list[index]))
        except (TypeError, ValueError):
            print("[실패] %s : %d번 자리의 값을 숫자로 읽을 수 없다. 받은 값: %r"
                  % (name, index, actual_list[index]))
            return False
    expected_c = [complex(value) for value in expected_list]

    # 4. 자리마다 차이를 구한다
    wrong = []
    worst_index = 0
    worst_diff = -1.0
    for index in range(n):
        diff = abs(actual_c[index] - expected_c[index])
        limit = abs_tol + rel_tol * abs(expected_c[index])
        if math.isnan(diff) or diff > limit:
            wrong.append(index)
        if math.isnan(diff):
            diff = math.inf
        if diff > worst_diff:
            worst_diff = diff
            worst_index = index

    # 5. 결과를 알린다
    if len(wrong) == 0:
        print("[통과] %s : %d개 모두 일치 (가장 큰 차이 %.3e, %d번 자리)"
              % (name, n, worst_diff, worst_index))
        return True

    # 양쪽 모두 허수부가 없으면 실수로만 보여 준다
    real_only = (all(value.imag == 0.0 for value in expected_c)
                 and all(value.imag == 0.0 for value in actual_c))
    print("[실패] %s : %d개 중 %d개가 다르다 (허용 오차 %g + %g x |기대값|)"
          % (name, n, len(wrong), abs_tol, rel_tol))
    print("    %6s  %-36s %-36s %s" % ("자리", "기대값", "실제값", "차이"))
    for index in wrong[:max_show]:
        print("    %6d  %-36s %-36s %.3e"
              % (index, _text(expected_c[index], real_only), _text(actual_c[index], real_only),
                 abs(actual_c[index] - expected_c[index])))
    if len(wrong) > max_show:
        print("    ... 그 밖에 %d개 (처음 다른 자리 %d, 마지막 다른 자리 %d)"
              % (len(wrong) - max_show, wrong[0], wrong[-1]))
    print("    차이가 가장 큰 자리: %d번" % worst_index)
    print("        기대값 %s" % _text(expected_c[worst_index], real_only))
    print("        실제값 %s" % _text(actual_c[worst_index], real_only))
    for hint in _find_hints(actual_c, expected_c, abs_tol, rel_tol):
        print("    힌트: %s" % hint)
    return False


def check_function(func, cases, max_show=DEFAULT_MAX_SHOW):
    """함수(func)에 검사 묶음(cases)의 입력을 하나씩 넣어 결과를 기대값과 비교한다.

    func 는 입력 리스트 하나를 받아 결과 리스트를 돌려주는 함수여야 한다.
    모든 항목이 통과하면 True 를 돌려준다.
    """
    passed = 0
    for case in cases:
        # 복사본을 넘긴다. 함수가 입력을 고쳐도 벡터 원본은 바뀌지 않는다
        values = list(case["input"])
        try:
            actual = func(values)
        except Exception:
            print("[실패] %s : 함수를 실행하다가 오류가 났다." % case["name"])
            for line in traceback.format_exc().rstrip().split("\n"):
                print("    " + line)
            continue
        ok = compare(case["name"], actual, case["expected"],
                     abs_tol=case.get("abs_tol", DEFAULT_ABS_TOL),
                     rel_tol=case.get("rel_tol", DEFAULT_REL_TOL),
                     max_show=max_show)
        if ok:
            passed += 1
    print("결과: %d개 중 %d개 통과" % (len(cases), passed))
    return passed == len(cases)


def check_window(values, max_show=DEFAULT_MAX_SHOW):
    """직접 만든 윈도우 512개를 기대값과 비교한다."""
    ok = compare("window/hanning_512", values, data.WINDOW_512,
                 abs_tol=data.WINDOW_ABS_TOL, rel_tol=0.0, max_show=max_show)
    if not ok:
        print("    힌트: 기대값은 대칭형이다. 분모가 (길이 - 1) = 511 인지 확인한다.")
    return ok


def get_case(name):
    """이름으로 검사 항목 하나를 찾는다. 예: get_case("fft/sine_1khz")"""
    for case in all_cases():
        if case["name"] == name:
            return case
    raise KeyError("그런 이름의 검사 항목이 없다: %s" % name)


def all_cases():
    """모든 검사 항목을 한 리스트로 돌려준다."""
    return (data.FFT_CASES + data.FFT_CASES_SMALL + data.IFFT_CASES
            + data.WINDOWED_CASES + data.ANALYSIS_CASES)


def list_cases():
    """검사 항목의 이름과 설명을 출력한다."""
    for case in all_cases():
        print("%-28s 입력 %4d개, 기대값 %4d개  %s"
              % (case["name"], len(case["input"]), len(case["expected"]), case["note"]))
    print("%-28s 기대값 %4d개  대칭형 Hanning 윈도우" % ("window/hanning_512", len(data.WINDOW_512)))


# ---------------------------------------------------------------------------
# 2. 원본과 복원 비교 (복원율)
# ---------------------------------------------------------------------------

def compare_samples(name, original, restored, tol=0, max_show=DEFAULT_MAX_SHOW):
    """원본 샘플과 복원 샘플을 비교하고 결과를 사전(dict)으로 돌려준다.

    여섯 가지를 잰다.
      1. 그대로 비교한 일치율    : 같은 위치끼리 값이 같은 샘플의 비율. 밀리면 0 에 가깝다
      2. 밀림과 부호             : 복원이 몇 샘플 늦거나 이른지, 부호가 뒤집혔는지
      3. 밀림을 맞춘 뒤 일치율   : 밀림을 없애고 다시 비교한 비율. 이 값이 복원율이다
      4. 크기 비                 : 복원이 원본의 몇 배인지
      5. 파형 유사도             : 밀림을 맞춘 뒤의 상관계수. 작은 오차에는 거의 줄지 않는다
      6. 스펙트럼 유사도         : 주파수별 크기만 비교한다. 위상은 보지 않는다

    차이가 tol 이하이면 일치로 본다. 정수끼리는 tol=0 (완전히 같아야 일치).
    반올림하기 전의 실수 값을 비교할 때는 tol=0.5 처럼 준다.
    """
    a = np.asarray(list(original), dtype=float)
    b = np.asarray(list(restored), dtype=float)
    result = {
        "percent": 0.0,             # 복원율. 밀림을 맞춘 뒤 일치율 (원본 개수 기준)
        "overlap_percent": 0.0,     # 밀림을 맞춘 뒤 일치율 (겹친 구간 기준)
        "plain_percent": 0.0,       # 그대로 비교한 일치율 (원본 개수 기준)
        "shift": 0,                 # 밀림. 양수면 복원이 늦다
        "sign": 1,                  # -1 이면 부호가 반대다
        "gain": 0.0,                # 크기 비. 복원 / 원본
        "waveform_percent": 0.0,    # 파형 유사도
        "spectrum_percent": 0.0,    # 스펙트럼 유사도
        "verdict": "",              # 판정
    }
    if len(a) == 0 or len(b) == 0:
        result["verdict"] = "비교할 샘플이 없다"
        print("[복원율] %s : 원본 %d개, 복원 %d개. %s." % (name, len(a), len(b), result["verdict"]))
        return result
    if np.isnan(b).any() or np.isinf(b).any():
        result["verdict"] = "복원에 nan 또는 inf 가 있다"
        print("[복원율] %s : %s. 0 으로 나누는 곳이 있는지 확인한다." % (name, result["verdict"]))
        return result

    total = len(a)

    # 그대로 비교
    plain = _count_same(a, b, 0, 1, tol)
    result["plain_percent"] = 100.0 * plain["same"] / total

    # 밀림과 부호를 찾아 맞춘 뒤 비교
    shift, sign = _find_alignment(a, b, tol)
    aligned = _count_same(a, b, shift, sign, tol)
    result["shift"] = shift
    result["sign"] = sign
    result["percent"] = 100.0 * aligned["same"] / total
    if aligned["compared"] > 0:
        result["overlap_percent"] = 100.0 * aligned["same"] / aligned["compared"]

    # 크기 비와 파형 유사도는 밀림을 맞춘 뒤 겹친 구간에서, 스펙트럼 유사도는 신호 전체에서 잰다
    result["gain"] = _gain(a, b, shift, sign)
    result["waveform_percent"] = _waveform_percent(a, b, shift, sign)
    result["spectrum_percent"] = _spectrum_percent(a, b)
    result["verdict"] = _verdict(result, len(a), len(b))

    # 알린다
    print("[복원율] %s : %.4f %%" % (name, result["percent"]))
    print("    그대로 비교       : %9.4f %%  (원본 %d개 중 %d개 일치)"
          % (result["plain_percent"], total, plain["same"]))
    print("    밀림              : %s" % _shift_text(shift, sign))
    print("    밀림을 맞춘 뒤    : %9.4f %%  (원본 %d개 중 %d개 일치)"
          % (result["percent"], total, aligned["same"]))
    print("    겹친 구간만 보면  : %9.4f %%  (겹친 %d개 중 %d개 일치)"
          % (result["overlap_percent"], aligned["compared"], aligned["same"]))
    print("    크기 비           : %9.4f    (복원 / 원본)" % result["gain"])
    print("    파형 유사도       : %9.4f %%" % result["waveform_percent"])
    print("    스펙트럼 유사도   : %9.4f %%" % result["spectrum_percent"])
    if len(b) != total:
        print("    길이가 다르다. 원본 %d개, 복원 %d개." % (total, len(b)))
    print("    판정: %s" % result["verdict"])

    # 밀림을 맞춘 뒤에도 다른 샘플을 보여 준다
    wrong = aligned["wrong"]
    if len(wrong) > 0:
        print("    밀림을 맞춘 뒤에도 다른 샘플 %d개 (허용 차이 %g)" % (len(wrong), tol))
        print("    %10s  %-16s %-16s %s" % ("원본 위치", "원본", "복원", "차이"))
        for index in wrong[:max_show]:
            value = sign * b[index + shift]
            print("    %10d  %-16s %-16s %g"
                  % (index, _number(a[index]), _number(value), value - a[index]))
        if len(wrong) > max_show:
            print("    ... 그 밖에 %d개" % (len(wrong) - max_show))
        print("    처음 다른 위치 %d, 마지막 다른 위치 %d" % (wrong[0], wrong[-1]))
        # 복원 값이 16bit 범위의 끝에 몰려 있는지 본다
        values = b[wrong + shift]
        clipped = int(np.sum((values == SAMPLE_MIN) | (values == SAMPLE_MAX)))
        if clipped >= 0.1 * len(wrong):
            print("    힌트: 다른 샘플 중 %d개가 %d 또는 %d 이다. 값이 너무 커서 잘렸을 수 있다."
                  % (clipped, SAMPLE_MIN, SAMPLE_MAX))
            print("          윈도우 합으로 나누는지, N 으로 나누는지 확인한다.")
    return result


def compare_wav(original_path, restored_path, max_show=DEFAULT_MAX_SHOW):
    """WAV 파일 두 개를 비교하고 결과를 사전(dict)으로 돌려준다.

    먼저 두 파일을 바이트 단위로 비교한다(filecmp). 전부 같으면 완전 복원으로 보고 끝낸다.
    다르면 샘플을 compare_samples 로 비교해 어디가 얼마나 다른지 알린다.

    16bit PCM 만 받는다. 파일을 읽지 못하면 이유를 알리고 None 을 돌려준다.
    채널이 둘 이상이면 파일에 놓인 순서대로(채널이 번갈아) 비교한다.
    돌려주는 사전은 compare_samples 의 것에 "file_same" (파일이 같은가)을 더한 것이다.
    """
    try:
        original_info, original = _read_wav(original_path)
        restored_info, restored = _read_wav(restored_path)
        # shallow=False: 크기와 수정 시각만 보지 않고 내용을 끝까지 읽어 비교한다
        file_same = filecmp.cmp(original_path, restored_path, shallow=False)
        same_path = os.path.samefile(original_path, restored_path)
    except FileNotFoundError as error:
        print("[오류] 파일이 없다: %s" % error.filename)
        return None
    except (wave.Error, EOFError, ValueError) as error:
        print("[오류] WAV 를 읽지 못했다: %s" % error)
        return None

    print("원본 %s : 채널 %d, 샘플 폭 %d바이트, %d Hz, 샘플 %d개"
          % (original_path, original_info["channels"], original_info["width"],
             original_info["rate"], len(original)))
    print("복원 %s : 채널 %d, 샘플 폭 %d바이트, %d Hz, 샘플 %d개"
          % (restored_path, restored_info["channels"], restored_info["width"],
             restored_info["rate"], len(restored)))
    for key, label in (("channels", "채널 수"), ("rate", "샘플링 주파수")):
        if original_info[key] != restored_info[key]:
            print("    주의: %s가 다르다. 원본 %d, 복원 %d"
                  % (label, original_info[key], restored_info[key]))
    if same_path:
        print("    주의: 원본과 복원이 같은 파일이다. 자기 자신과 비교하고 있다.")

    # 1차: 파일 전체를 비교한다. 같으면 샘플을 따로 비교하지 않는다
    if file_same and len(original) > 0:
        print("    파일 비교: 같다. 파일 전체가 바이트 단위로 같다.")
        result = {
            "percent": 100.0,
            "overlap_percent": 100.0,
            "plain_percent": 100.0,
            "shift": 0,
            "sign": 1,
            "gain": 1.0,
            "waveform_percent": 100.0,
            "spectrum_percent": 100.0,
            "verdict": "완전 복원",
            "file_same": True,
        }
        print("[복원율] %s : %.4f %%" % (restored_path, result["percent"]))
        print("    판정: %s" % result["verdict"])
        return result

    # 2차: 파일이 다르면 샘플을 비교해 원인을 찾는다
    if not file_same:
        print("    파일 비교: 다르다. 샘플을 비교한다.")
    result = compare_samples(restored_path, original, restored, tol=0, max_show=max_show)
    result["file_same"] = file_same
    if not file_same and result["verdict"] == "완전 복원":
        print("    샘플은 전부 같다. 파일에서 샘플이 아닌 부분(헤더 등)이 다르다.")
    return result


# ---------------------------------------------------------------------------
# 아래는 이 파일 안에서만 쓰는 도우미다
# ---------------------------------------------------------------------------

def _text(value, real_only=False):
    """값 하나를 읽기 좋은 글자로 바꾼다. 유효 숫자 12자리까지 보여 준다."""
    if real_only:
        return "%.12g" % value.real
    return "%.12g%+.12gj" % (value.real, value.imag)


def _number(value):
    """샘플 값 하나를 글자로 바꾼다."""
    if float(value) == int(value):
        return "%d" % int(value)
    return "%.12g" % value


def _all_close(actual, expected, abs_tol, rel_tol):
    """모든 자리가 허용 오차 안에서 같은지 본다."""
    for index in range(len(expected)):
        diff = abs(actual[index] - expected[index])
        if math.isnan(diff) or diff > abs_tol + rel_tol * abs(expected[index]):
            return False
    return True


def _find_hints(actual, expected, abs_tol, rel_tol):
    """결과가 기대값을 어떤 식으로 바꾼 것과 같은지 찾아 본다.

    기대값을 몇 배 하거나, 켤레를 취하거나, 순서를 뒤집은 것과 비교한다.
    비교만 한다. 변환을 계산하지 않는다.
    """
    n = len(expected)
    hints = []
    if any(math.isnan(abs(value)) for value in actual):
        hints.append("결과에 nan 이 있다. 0 으로 나누었거나 초기화하지 않은 값이 있는지 확인한다.")
        return hints
    if any(math.isinf(abs(value)) for value in actual):
        hints.append("결과에 inf 가 있다. 값이 넘쳤는지 확인한다.")
        return hints
    if all(value == 0 for value in actual):
        hints.append("결과가 전부 0 이다. 계산한 값을 결과 리스트에 넣고 있는지 확인한다.")
        return hints

    has_imag = any(value.imag != 0.0 for value in expected)
    shapes = [("", expected)]
    if has_imag:
        shapes.append(("허수부의 부호가 반대다",
                       [value.conjugate() for value in expected]))
    shapes.append(("순서가 뒤집혀 있다 (k번 자리에 N-k번 자리의 값이 있다)",
                   [expected[(n - index) % n] for index in range(n)]))
    scales = [(1.0, ""),
              (float(n), "크기가 기대값의 N배(%d배)다" % n),
              (1.0 / n, "크기가 기대값의 1/N배(1/%d배)다" % n)]

    for shape_text, shape_values in shapes:
        for scale, scale_text in scales:
            if shape_text == "" and scale_text == "":
                continue
            candidate = [value * scale for value in shape_values]
            if _all_close(actual, candidate, abs_tol * max(scale, 1.0), rel_tol):
                parts = [text for text in (shape_text, scale_text) if text != ""]
                advice = []
                if shape_text != "":
                    advice.append("지수(회전 인자)의 부호를 확인한다")
                if scale_text != "":
                    advice.append("N 으로 나누는 곳을 확인한다")
                hints.append("%s. %s." % (", ".join(parts), ", ".join(advice)))

    if len(hints) == 0:
        # 위에 없는 배율인지 본다. 기대값이 가장 큰 자리에서 비를 구한다
        peak = max(range(n), key=lambda index: abs(expected[index]))
        if abs(expected[peak]) > 0.0:
            ratio = actual[peak] / expected[peak]
            if abs(ratio - 1.0) > 1e-6 and abs(ratio) > 1e-12:
                candidate = [value * ratio for value in expected]
                if _all_close(actual, candidate, abs_tol * max(abs(ratio), 1.0), 1e-6):
                    hints.append("모든 자리가 기대값의 (%s)배다. 곱하거나 나누는 상수를 확인한다."
                                 % _text(ratio, abs(ratio.imag) < 1e-12))
    return hints


def _overlap(length_a, length_b, shift):
    """원본의 어느 구간이 복원과 겹치는지 돌려준다. 원본[위치] 와 복원[위치 + shift] 를 맞춘다."""
    start = max(0, -shift)
    stop = min(length_a, length_b - shift)
    return start, stop


def _count_same(a, b, shift, sign, tol):
    """원본[위치] 와 sign x 복원[위치 + shift] 를 비교해 같은 개수와 다른 위치를 돌려준다."""
    start, stop = _overlap(len(a), len(b), shift)
    if stop <= start:
        return {"compared": 0, "same": 0, "wrong": np.zeros(0, dtype=int)}
    diff = np.abs(sign * b[start + shift:stop + shift] - a[start:stop])
    wrong = np.nonzero(diff > tol)[0] + start
    return {"compared": stop - start, "same": (stop - start) - len(wrong), "wrong": wrong}


def _find_alignment(a, b, tol):
    """복원이 몇 샘플 밀렸는지, 부호가 뒤집혔는지 찾는다. (밀림, 부호) 를 돌려준다.

    두 신호를 조금씩 어긋나게 겹쳐 가며 닮은 정도(상관)를 구하고, 가장 닮은 어긋남을 고른다.
    상관은 numpy 의 FFT 로 한꺼번에 구한다. 후보 여러 개를 실제로 비교해 일치가 가장 많은 것을 고른다.
    """
    size = 1
    while size < len(a) + len(b):
        size = size * 2
    spectrum_a = np.fft.rfft(a, size)
    spectrum_b = np.fft.rfft(b, size)
    # correlation[k] = sum(a[n] * b[n + k]). 음수 k 는 뒤쪽에 놓인다
    correlation = np.fft.irfft(np.conj(spectrum_a) * spectrum_b, size)
    if not np.any(np.abs(correlation) > 0.0):
        return 0, 1

    order = np.argsort(np.abs(correlation))[::-1][:SHIFT_CANDIDATE_COUNT]
    candidates = [(0, 1), (0, -1)]
    for index in order:
        shift = int(index) if index < size // 2 else int(index) - size
        if -len(a) < shift < len(b):
            candidates.append((shift, 1 if correlation[index] >= 0.0 else -1))

    best = (0, 1)
    best_key = None
    for shift, sign in candidates:
        counted = _count_same(a, b, shift, sign, tol)
        # 겹친 구간이 원본의 절반 이상이고 그 안이 전부 같으면 먼저 고른다
        perfect = (counted["same"] == counted["compared"]
                   and counted["compared"] * 2 >= len(a))
        # 겹친 구간의 절반 이상이 같으면 일치한 개수로 견준다
        enough = (counted["same"] * 2 >= counted["compared"]
                  and counted["compared"] * 2 >= len(a))
        # 그렇지 않으면 닮은 정도로 견준다. 끝으로 밀림이 작은 것, 부호가 그대로인 것을 고른다
        key = (perfect, enough, counted["same"] if enough else 0,
               round(_waveform_percent(a, b, shift, sign), 3), counted["same"],
               -abs(shift), sign)
        if best_key is None or key > best_key:
            best_key = key
            best = (shift, sign)
    return best


def _gain(a, b, shift, sign):
    """복원이 원본의 몇 배인지 돌려준다. 밀림을 맞춘 뒤 겹친 구간에서 잰다."""
    start, stop = _overlap(len(a), len(b), shift)
    if stop <= start:
        return 0.0
    part_a = a[start:stop]
    part_b = sign * b[start + shift:stop + shift]
    energy = float(np.sum(part_a * part_a))
    if energy == 0.0:
        return 0.0
    return float(np.sum(part_a * part_b)) / energy


def _waveform_percent(a, b, shift, sign):
    """밀림을 맞춘 뒤의 상관계수를 퍼센트로 돌려준다. 0 보다 작으면 0 으로 한다."""
    start, stop = _overlap(len(a), len(b), shift)
    if stop <= start:
        return 0.0
    part_a = a[start:stop]
    part_b = sign * b[start + shift:stop + shift]
    energy = float(np.sum(part_a * part_a)) * float(np.sum(part_b * part_b))
    if energy == 0.0:
        return 100.0 if np.array_equal(part_a, part_b) else 0.0
    value = float(np.sum(part_a * part_b)) / math.sqrt(energy)
    return 100.0 * max(0.0, min(1.0, value))


def _average_spectrum(values):
    """신호를 512개씩(256개 간격) 잘라 주파수별 크기를 구하고, 구간들의 평균을 돌려준다.

    검증용이다. numpy 의 윈도우와 FFT 를 쓴다.
    """
    length = SPECTRUM_FRAME
    if len(values) < length:
        padded = np.zeros(length)
        padded[:len(values)] = values
        values = padded
    window = np.hanning(length)
    power = np.zeros(length // 2 + 1)
    count = 0
    for start in range(0, len(values) - length + 1, length // 2):
        spectrum = np.fft.rfft(values[start:start + length] * window)
        power = power + np.abs(spectrum) ** 2
        count += 1
    return np.sqrt(power / count)


def _spectrum_percent(a, b):
    """주파수별 크기만 비교한 유사도를 퍼센트로 돌려준다.

    신호 전체의 평균 스펙트럼끼리 비교한다. 위상과 밀림에 거의 영향을 받지 않는다.
    """
    size_a = _average_spectrum(a)
    size_b = _average_spectrum(b)
    energy = float(np.sum(size_a * size_a))
    if energy == 0.0:
        return 100.0 if float(np.sum(size_b * size_b)) == 0.0 else 0.0
    error = float(np.sum((size_a - size_b) ** 2))
    return 100.0 * max(0.0, 1.0 - error / energy)


def _shift_text(shift, sign):
    """밀림과 부호를 글자로 바꾼다."""
    if shift > 0:
        text = "복원이 %d샘플 늦다" % shift
    elif shift < 0:
        text = "복원이 %d샘플 이르다" % (-shift)
    else:
        text = "없다"
    if sign < 0:
        text = text + ", 부호가 반대다"
    return text


def _verdict(result, length_a, length_b):
    """잰 값으로 한 줄 판정을 만든다."""
    if result["plain_percent"] == 100.0 and length_a == length_b:
        return "완전 복원"
    if result["overlap_percent"] == 100.0:
        if result["sign"] < 0:
            return "값은 같고 부호가 반대다. 부호를 뒤집는 곳이 있는지 확인한다"
        if result["shift"] != 0:
            return "값은 같고 위치만 밀렸다. 겹쳐 더할 때의 위치를 확인한다"
        return "겹친 구간은 같고 길이가 다르다. 샘플 수를 확인한다"
    if result["waveform_percent"] >= NEARLY_SAME_PERCENT:
        # 대부분의 샘플이 다르고 크기 비가 1 이 아니면 크기가 다른 것으로 본다
        if (result["overlap_percent"] < PARTLY_PERCENT
                and abs(result["gain"] - 1.0) > GAIN_TOLERANCE):
            return ("모양은 같고 크기가 %.4f배다. 곱하거나 나누는 상수를 확인한다"
                    % result["gain"])
        return "거의 같다. 작은 오차가 있다"
    if (result["spectrum_percent"] >= SPECTRUM_SAME_PERCENT
            and result["waveform_percent"] < WAVEFORM_DIFFERENT_PERCENT):
        return "주파수별 크기는 같고 파형이 다르다. 위상이 달라졌다"
    if result["overlap_percent"] >= PARTLY_PERCENT:
        return "일부만 복원되었다. 다른 위치를 확인한다"
    return "복원되지 않았다"


def _read_wav(path):
    """WAV 파일을 읽어 (정보, 샘플 리스트)를 돌려준다. 16bit PCM 만 받는다."""
    with wave.open(path, "rb") as wav_file:
        info = {
            "channels": wav_file.getnchannels(),
            "width": wav_file.getsampwidth(),
            "rate": wav_file.getframerate(),
        }
        raw = wav_file.readframes(wav_file.getnframes())
    if info["width"] != 2:
        raise ValueError("%s 의 샘플 폭이 %d바이트다. 2바이트(16bit)만 비교할 수 있다."
                         % (path, info["width"]))
    samples = array.array("h")
    samples.frombytes(raw)
    if sys.byteorder == "big":
        samples.byteswap()
    return info, list(samples)
