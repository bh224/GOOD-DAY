# GOOD-DAY





☀️🎶 make your day better...[good-day!](https://www.good-day.today/)

##### 🚩 프로젝트소개
- 개인 또는 그룹 간 일정관리 공유 사이트

##### 🗓️ 개발기간
- 2022.12. (for 2wks)
- Keep updating

##### 🤝 멤버구성
- 1인 프로젝트
- Role: 기획 - 배포

##### 🛠 ️개발환경 
- ️➡️ Backend
  - Python 3.9
  - Django 4.14
  - Django Rest Framwork
- ️➡️ Frontend : [소스코드](https://github.com/bh224/GOOD_DAY_FRONTEND)
  - ReactJS
  - TypeScript
  - ChakraUI
- ️➡️ Database
MySQL
![ERD_221227](https://user-images.githubusercontent.com/104023868/209669433-b89f7946-496d-46e9-a4c8-b81b98bcf822.jpg)

##### 🌏 배포
- AWS EC2 (백엔드 서버)
  - Nginx
  - Gunicorn
- AWS S3 + CloudFront (프론트엔드 서버)
  - Github Actions

##### 📌 주요기능
- 로그인
  - ID중복검사 
  - 구글, 네이버, 카카오 소셜로그인
- 일정등록 및 관리
  - task(그룹일정) / todo / private 일정 타입 분리
  - yet(그룹일정) / doing / done 일정 진행상황 관리
  - 오늘의 일정 진행률 표시
  - 과거에 등록한 일정 날짜별 조회
- 그룹일정
  - 그룹 유저에게 일정 부여
  - 그룹 유저간 일정 및 투데이(on/off) 표시
  - 내가 가입한 그룹 유저의 오늘 일정 확인
