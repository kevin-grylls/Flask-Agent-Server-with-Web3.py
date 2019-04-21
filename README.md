### Flask Server with Web3.py

---

##### Agent Server For Smart Wallet

- 이더리움 트랜잭션을 실행할 수 있는 플라스크 에이전트 서버입니다.
- 개인 계정 생성 시 어드레스와 개인키를 같이 저장합니다.
- SQLite3 기반의 파일 DB를 활용합니다.

##### 설치방법

- 의존성 설치

```sh
$ pip install -r requirements.txt
```

- 아래 커맨드로 실행 (포트: 8000)

```sh
$ python3 agent-web3.py
```

- 포트 변경이나 가나슈 / EVM 연결설정은 소스코드에 주석으로 표기되어 있습니다.
