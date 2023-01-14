# Pi MJPEG Server

An extremely lightweight hardware-accelerated MJPEG streaming server for Raspberry Pi + Camera Module with `Flask` & `libcamera` API.

## Caution
There is no security in this code to prevent any kind of attack. Consider implementing basic authentication with HTTPS if possible!

## Setup
- Update your Raspbery Pi to latest official OS. Use Lite for lowest resource usage!
- Update packages with :
  - `sudo apt update`
  - `sudo apt upgrade -y`
  - `sudo apt dist-upgrade -y`
- Install Python packages with :
  - `sudo apt install python3-pip -y`
  - `sudo apt install python3-picamera2 --no-install-recommends`
- Enable `I2C` via `raspi-config`
- `git clone `https://github.com/kingkingyyk/Pi-MJPEG-Server.git`
- `cd Pi-MJPEG-Server`
- Update `mjpeg_server.py` if needed. There are some configurations available such as resolution.
- Move python script to somewhere safe: `cp mjpeg_server.py /usr/local/bin`
- Install required python packages: `python3 -m pip install -r requirements.txt`
- Create an auto start service with: 
  - `sudo mv mjpeg_server.service /etc/systemd/system`
  - `sudo systemctl daemon-reload`
  - `sudo systemctl start mjpeg_server`
  - `sudo systemctl enable mjpeg_server`
- Verify the server is running fine with :
  - `sudo systemctl status mjpeg_server`
  - Open your browser and visit address `http://<Pi IP>:<8764/Port>/`

## Motioneye Support
This code is tested on work with [motioneye](https://github.com/motioneye-project/motioneye). Just add this server url as network camera.

## Support
The code is tested to work on Pi 4 + Camera Module v3. (~4% CPU usage for single connection, 1% more for every connection)

## Bonus
If you use Pi Zero, you still can run this code, but run motioneye in a more powerful machine such as Pi 4 or x86 machine. This helps reducing the chance of throttling due to high temperature.
