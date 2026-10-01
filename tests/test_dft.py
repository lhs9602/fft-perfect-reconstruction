# src/dft.py 의 시험. 실행: 프로젝트 폴더에서 .venv\Scripts\python.exe -m pytest -v -k dft
import dft
import testvec as tv


# 느린 DFT 와 역 DFT
# check_function 이 입력을 함수에 넣고, 결과를 기대값과 자리마다 비교한다. 다 맞으면 True
def test_dft_small():
    assert tv.check_function(dft.dft, tv.FFT_CASES_SMALL)  # 길이 8 한 개. 이것부터 맞춘다


def test_dft():
    assert tv.check_function(dft.dft, tv.FFT_CASES)  # 길이 512 다섯 개 (임펄스, 직류, 사인, 잡음, 말소리 닮은 신호)


def test_idft():
    assert tv.check_function(dft.idft, tv.IFFT_CASES)  # 길이 512 다섯 개


def test_dft_idft_roundtrip():
    x = tv.get_case("fft/speechlike")["input"]  # 길이 512 입력 하나
    assert tv.compare("dft -> idft", dft.idft(dft.dft(x)), x)  # DFT 뒤 역 DFT 를 하면 입력으로 돌아온다
