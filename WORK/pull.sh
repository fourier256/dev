#!/bin/bash

# SFTP 서버 접속 정보
HOST="43.201.147.78"
USER="ubuntu"
PASS="your_password"
REMOTE_DIR="WORK/"
LOCAL_DIR="your_local_directory"

# SFTP 명령어 자동화
sftp -oBatchMode=no -i ./MY_EC2_KEY.pem -b - $USER@$HOST <<EOF
cd $REMOTE_DIR
mget -r *
exit
EOF

echo "파일 다운로드 완료"
