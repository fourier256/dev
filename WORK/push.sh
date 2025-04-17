#!/bin/bash

# SFTP 접속 정보
HOST="43.201.147.78"
USER="ubuntu"
REMOTE_DIR="WORK"
LOCAL_DIR="."

# SFTP를 사용하여 파일 다운로드
sftp -i ~/.ssh/MY_EC2_KEY.pem $USER@$HOST <<EOF
cd $REMOTE_DIR
lcd $LOCAL_DIR
mput -r *
bye
EOF
