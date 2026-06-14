# 以官方 Airflow 3.2.1 作為基底映像
FROM apache/airflow:3.2.1

# 切換為 root，才有權限修改系統群組
USER root

# 修正容器內 docker group 的 GID，使其與宿主機一致
# 目的：讓 airflow 使用者能透過 /var/run/docker.sock 操作宿主機 Docker
RUN groupdel docker 2>/dev/null || true && \
    groupadd -g 1001 docker && \
    usermod -aG docker airflow && \
    usermod -aG docker default || \
    sed -i 's/^docker:.*/&,default/' /etc/group

# 切回 airflow 使用者（避免以 root 權限運行容器，較安全）
USER airflow

# 複製套件清單到容器內
COPY requirements.txt /opt/airflow/requirements.txt

# 預先安裝所需 Python 套件（build 時執行一次，比環境變數方式更有效率）
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt