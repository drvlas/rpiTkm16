# rpiTkm16
Raspberry Pi3 as an Operator panel for Board14 TKM16 project

$ sudo sed -i -e '$a//192.168.0.100/Volume_1 /mnt/vol1 cifs credentials=/home/vpe/my-sys/.vpe,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0' /etc/fstab
$ sudo sed -i -e '$a//192.168.0.100/Volume_2 /mnt/vol2 cifs credentials=/home/vpe/my-sys/.vpe,iocharset=utf8,file_mode=0775,dir_mode=0775 0 0' /etc/fstab

Keys' commands from PC to ADC

rb_tare         toggle Ctrl bit

MAIN
bp_dose_nom     show_numpad(self, 'DOZA1') = numpad + write_dregs()
pb_run          set KEYS.K_RUN
pb_stop         set KEYS.K_STOP
pb_unload       set KEYS.K_UNLOAD

PARS
pb_parv         show_numpad(self, key(parn)) = numpad + write_dregs
pb_parn         show_numpad(self, 'PARN') = numpad + write_dregs
pb_prev         parn--
pb_next         parn++

CLBR
pb_clbr0        set KEYS.K_CLB0
pb_clbr1        set KEYS.K_CLB1
pb_clbr2        set KEYS.K_CLB2
pb_clbr3        set KEYS.K_CLB3
pb_zero         set KEYS.K_ZERO

MANU
rb_out6         set/reset K_OUT6
rb_out7         set/reset K_OUT7
rb_out8         set/reset K_OUT8
rb_out9         set/reset K_OUT9
rb_outa         set/reset K_OUTa
rb_outb         set/reset K_OUTb
rb_outc         set/reset K_OUTc
rb_outd         set/reset K_OUTd

LOGO
rb_master       set K_MAST

Menu actions



