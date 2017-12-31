# rpiTkm16
Raspberry Pi3 as an Operator panel for Board14 TKM16 project

$ sudo sed -i -e '$a//192.168.0.100/Volume_1 /mnt/vol1 cifs credentials=/home/vpe/my-sys/.vpe,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0' /etc/fstab
$ sudo sed -i -e '$a//192.168.0.100/Volume_2 /mnt/vol2 cifs credentials=/home/vpe/my-sys/.vpe,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0' /etc/fstab

