# -*- coding: utf-8 -*-
# 既存 soxl_notify.py を全文置換。末尾の END 行までコピー。
# 確認: python soxl_notify.py --check-only / 展開: --show-source
import ast as _ma,base64 as _mb,hashlib as _mh,linecache as _mc,lzma as _mz,sys as _ms
from pathlib import Path as _mp
_MOBILE_BUILD = 'v20-close-check-20261106-mobile4'
try:
    _mlines = _mp(__file__).read_text(encoding='utf-8').splitlines()
    if '# END '+_MOBILE_BUILD not in [x.strip() for x in _mlines]:
        raise ValueError('末尾まで貼れていません')
    _mtext = ''.join(x.strip()[2:] for x in _mlines if x.strip().startswith('#|'))
    if len(_mtext) != 20390:
        raise ValueError('圧縮部分の文字数が違います')
    _mbytes = _mz.decompress(_mb.b85decode(_mtext))
    if _mh.sha256(_mbytes).hexdigest() != '91aebc7c31e3a5f9a0c262a484513ff7b230d90bdf180beebe0367dd0aa137e6':
        raise ValueError('内容が変わっています')
    _mobile_source = _mbytes.decode('utf-8')
    _mfile = '<'+_MOBILE_BUILD+'>'
except Exception as _merror:
    raise SystemExit('貼り付け内容が不完全か変化しています。末尾のEND行まで貼り直してください。'
                     +' ('+str(_merror)+')') from None
try:
    _mcode = compile(_mobile_source,_mfile,'exec')
except SyntaxError as _merror:
    raise SystemExit('内容照合は成功しましたが、展開コードの構文に問題があります。'
                     +'Python '+_ms.version.split()[0]+' / '+str(_merror)) from None
if __name__ == '__main__':
    if '--show-source' in _ms.argv:
        print(_ma.unparse(_ma.parse(_mobile_source)))
        raise SystemExit(0)
    print('【起動版】'+_MOBILE_BUILD+' / 内容確認OK',flush=True)
    if '--check-only' in _ms.argv:
        raise SystemExit(0)
_mc.cache[_mfile] = (len(_mbytes),None,_mobile_source.splitlines(True),_mfile)
exec(_mcode,globals())
if __name__ == '__main__':
    raise SystemExit(0)
#|{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;MH0`c3l88n@VT6Qap3Y@@2YR=<xD3-!$i)oz0TLXrElF34PU)11eJx9yG1{>JbsWO_oHW9+{kPO6LOOJ!VSBAnrf*
#|R>q!7FY9oID>Z3VDrA$fT+ykY+D{2Y0Z|D>v*&&-IlGb7+P)vEyisRe3|bddW3@{aSOl8u2a6DZ{!3)Qj6Yc@mV0sL9EO=LxZizyC-Blf^}FdfhEwBP7S$(a
#|n^62j<9}D86{8Sj;C3vT&Qf@QUlf#4&Jb(^&+Kpjn409AP{;;j450ou5A@^9p!or!^7~!7Ih7U7FnCQ0+06TV`?SEH@FravsNF8Q%*}R76?ITkW|I|2GHu`b
#|Esk)d;%cv_Z2dQ_!4~-XX8}Wi^!)up7YB*crhmI%c=d*}YO;;3fZxY2`c_6~JLHQv<g@SCgPv5O`Vq+IRKl&{Fhxxsgcn=kn%t*WybB3{(L3WE<P{xk7d?AJ
#|U5TUB6}0rl1G>-%hGVB)x)_TdiT{w{nfgmaVNpG^`xCvJ`=BIcPv3;T<^g6NFY|!_LLx7Hgo?ADZq^eQcXx>ZA|iw5$%_fmUUiJi)%VTQWs7us4(oA3t#L9w
#|o8o2Ert;hDMr3s=WKY@~&GgOKfR6!)_S{WNT2C)N`zCcOuyMT~(%t)v5lCB^Cuq=kFt{B-Fbh{@R|x<_%E>+kHi{=rS7%@8PW5~X4NkuGV3{?g){y4-+K78c
#|Jvx)pTqJxYsK1D^o(?B|bTOH9#I<y;_^Yu-qF{x2{p>$5dx=nj8O0!K5ng+53JB?Fni9dD%SW;)FS>}%_|Q+!b&IE;;`MkqHwLxE#EZo6aFo>ilGXJyxe_-u
#|LyX#4>Hjm<vym%nNx%drhhe~p*qB-zsR=>2(S6r!_ws0~BzFd2%Mnc&n`dOmu*BHGL1Q&8zs!v5P`=Ua|IUGZF}uk=g|iPh2_0R3+NtV|T20fLI-sJ8Q8;lg
#|^~0L;^NTrzrr_X=-gdgSp2Vn(#K;k{1P^lE(09`QM39NKXvt<)D3n2>hpQdPPdchyB<5TCKgU67WX&k~%ryYoW|Z-YxJ3uTh$^fgPOI$zudDlDp+>K8V?rh(
#|-e3|@F=oHAQ1s+{S;zD**U$zGLo8J|Ndd&vq3<^7`Ogh|Et@}_dK<Pbd>q3ln4^O^$C(HEanHtbT)SFOuOW;p9jVtwq`>Q!MFF3Pyhgh>&H}}!%e&N^)&-TF
#|0NB@D{vxSl?@O$Fx_zbC-{C!R2_GQhj%L$S2>OfL@>F1u=pd6X%s=MyYzb#aeiw(k66;I(g-}l&yH!0A=upmDA?2^ouO(Qzz0G6E8|?9RlNxnW&kqs+MzXs~
#|6|0@w<H3X=^~j9iJE5*GmDjlczIm6V`)-XtwP)~%#y%;5M-cW}iRRn`HUiGMJL#qvD+jTReIXO>6=)HV`n>@du4!l~eK5`*3#p1433hsnB8I!G{QMi2>Arx~
#|%ysX?<BR=N*6hme!-!Wb4jqFh&QOOJcNB8GDVRJNg~greu1(-G+;i8LV&KW64ZzBafxjb4(hQf>weUm?8jX17pODhXcIB|h0x0-vT2H{2$yUc8-lPvD^W=R#
#|R^DIYi@kjD4Ft449$Owl0s2b8Iv+F?57WxPNPzRpPywZMrX!N#k~*arGe$)yP7Kvns;(9%*i{iU%p&N0<~{uQrq|Mh@WfIwHy(q;f%`yketU^LuWzTIm)_$%
#|hOt+xEPq;9XCQ~_?D@SNfxNee%K<J})I#{k_juKA+wp_daXzCt2B;~=nV+g4F!wa`zogGE*9Pi4;ngjh;C*nr(*k%%oAIAFVOMg+b2Y-r*FNU2;{!fu4z&qF
#|JMnkwY~`U&1VLEYGs%*+*ph2jmcd+!VJSzE3PklXiH~T3;zznXn=?*?48Lty4{9r)%O#EW70TEjQ=48l@yqs86c>aH@$qLnvVMB&QoUpccWyv<O&G^6|N92m
#|haquV&Srk6v$E0lg^O3RnJ|-Fy%(_i6c@xiS>*Hg_UR+k5NljXA~N|MC1Ou_zc)U|(c8CySF+9|x1y~O$0JM95zu<l0zbPY0-X@=b!FcX534FK^fvP;a)(9a
#|3jCZ3-3*$i1W2#_tbnU9Q-ij04`5>6$5to(U^|tn+OTTOSZ$l5>;fh|C{lyMD^(f>CQ4}Zfi63U3qTlw0G46q0bgPh;Lc(0J)P>ue2xz`gE3*S)0Akg&lbjV
#|U^JFSt)nXz$<3+xNzX)1;Ib<1v9c6Bf4~-a<8#Mo`3+R_62!}~#<l~sINUZ)fNgsU64o^^Iq?$pYVAVMq|~~~z?Ude!oVu6mV(C-dA~HO=57fo==6`66V3^_
#|1{5Yqw$%Muq2m3F@+zkXVi&AQeaXL3y_6_aHqWckBww+l^Yj%^7H;QZq3%G%PMnn*{aJY3z)D5c=ZJVZ14@Y8#wQTj!j&&8s3O$>AjIch@ZKCDG?j;&RNp&N
#|#GS&z-rL<6l>s38uq_bMsDv$TVdstai4~og8Dw7JaqAgahzvs7EDEs)*~s};Nyk2w`Rht|{f*QNz?sf1dnbT@OWq8XCYK3~imiZud@Dk!N#QB&HuYrTzlL8!
#|-~rX-z3L&K6!(;`iK<xu(p?b9x6t;L74~4qz`0ve(nMt0oY?c(Qp<lzfMI?vbNl%pNCYj}F3m9FDSF@etrSRg;zom^C`X0OV0bGKR?P6x4KXF-Jf<@<EZ4`2
#|wH`MIiM!mx`TSo$<^ZY-%T;ub4omNDY|mzh8g8h;+K!Jz$=w)A2?5I?M(*hi^Qm*yQalB+e3By$IIMTzZoMz({>v#l?s+W$G&`@@4*$G?rR)0ZHSxBK{IBg?
#|B>6L0AXtYr!~kp`&1&W<&VqFyu@i1Kkqy^QAK3wnf5U^jT99F~ZCp@z+Ym3BAzSNa?kK9OHo|ZQL>G23vi)B!m52S6l7k0LCK5{~L-sbs4Iv5B9b)m+V*Il8
#|AO3^|PiS?VcTfZJ`Ii!QHFUjd0(@Zx8A9ZqLgd5Las@Dry->ljCtVoejGItGgvOp8Mw!P0EduG?9nqDlyq+U%=gdkO#RJ8A;(z&rBhdx!EAGem97dy=r5vwJ
#|d_q><e;dq$As%#Uj}+u_Is$a2Q6wIa41JLb@d@3eB$nFyP@fwLT`H!dpxybDZiOlA4yf&Rll88+kbt9uf`8jKN4q-PZy#E-C&hB;DRI}@h2GUCc5a^g%i@5N
#|T#GW1DR`eps+jdf@3cv-vpyUf{SAlKXuWj}r)e|j&}o-`S7-LQh3pV*IM;iVYmlpY#&w$=z#e%gWx`bxk$vXKq|Kbh<0yaLL~FNS=K)zBEwT&OqrkiQT`*V5
#|zDp;BgJJwC?VOKBLWIW9^H*M45o!Cj`2ybsN`5EMFP(@c+e8ti(U+q4%Z!q`=g8UhV^P!4v1dBelk7&;$aF4*eaJaI*Lz=scM@Jl;4)H5=M2aWg2Y5MmO8UL
#|Prlx!;v8Q0@tX8$DsM(JR<DnsjSxOBF$YS*%y%#(!TqIg(IjbjEe##%DH$dv{*O(f%RLW-0j$_M18O?KR@!Q1y!|~48H5VlPxSOdYeZx|aW?lYd`{8hM~~$O
#|hropCbP~(+fBbWRD(>gvB|r}RCi6Oo77kT&op(tkuae<~xp*gR&99Xqit9%yPXvw@cd^jBGuPA}{HIMtpDjQ`k518ai$n!^Iw#=TnSehS&ICkIp;4oRRq8~y
#|M#UQ&owrD^7xV-OUxU}Edsi6^@e8*ewYs%hr9gQ3Cm(>>dQC_ML}A%ZDKnn2MX_5Ij#E1TzlFF(Q=<6#?}l%PS?Dcla$wf3s!tGg=>*{M-rL<WZnPn@rWhW7
#|UK;E+u}8y0w(ak<2tkxZg@rXOv=vlR34cETP1iUiq6N_Yz33bgrTlNr9<l*nMGzj_5sV`aptaw6YbrJUG{x57>+~wWPwS;!>1l9>;xfSf06{EYQey*kZ<|bc
#|fNC0?#d-VbiKcV6TJGsvq*4^W8xxce-PWX+o7kaBQ1c&NHs5`ZM*m~3=UXU$b`VHmxasaA49`l-9T)JH!ZH6LgkT?+`FU%rua?w-;Kv>dwL>9Qu6^jMYucDJ
#|_wRFCr(<X}Q-RBUDOLKuD768S40I`t?x)TQB5ED<2W+1i8IDqE$TaT8JFqw?X?F#}Ro34*1Dvcm>r4!wT^^eBcUccWXr&J56-$9zOyR$CrEagSdVrm)$r+&6
#|2=W^#x(>cw#&ue%Fsz#H7(<*im_l+2TB6W7ID#k|`;*gshnRB}Y*Zu?wSOx52JD(GhiX;w2&?bE3=o7emU8+bGiZI)vLO#$J}3u%s<TH^>~L6anh;SE2KWag
#|IlHW9o>@28@MjLAl~@S{m4ww)iLZPMFg*cj*1+@n6WVTS_gDA*zKa~J_J6C8kTK+NDB36`A{H6WxR7nXDTy_rquQN$Ru*i0$m=ee51IvMuEZ)oaPBK|j`7PU
#|#UJLJ2U>w=D>D1h3t!T>;3qIL7-oy?szRW0?AhOUvi;0d_{Nt&KhOMr7uB=wsZ73U(5lChD(j6IHAd|IPpUq^Ut=P{-X%_fPKr|KhZz{I)28K`t$T(}en-&~
#|tT~S8n*@#O2KyK0On-al1|u~xcD{XwZ!0DJNT+d}3brLM2SFi~5kIw!s_H>-0>c@>4RZ5UYePMdiyh%I8R6X(Zk{V#GJ@e9!I=nC8B06bH=bot7?#X|`SroA
#|obd(qn))HS&MQq-iksqz(v4A7R{_zMiX)P*o>JGo=MStF5w7{kw8%O8YJa%r(6y00&h(ONf;g&7A+>=mA_Sw4^pjO>tc5mH42%~wXo?ZTVBT&!F=2Pa!dWMt
#|y7N;s3ltMbKA!_@_7y){Ody05L!}V4dr*{(2s?eD+|b-wuyii#)ly(CE%8gE&Ze!XY2s$4rVu17G5Q-gXt>B&w&4x7qHV>@T^3Ey%lK$00`*Ar87Jk`2?;_?
#|Lwb*^L0BE#2oF0(gD@otoqEo6C;=XkHc9?W^}ut%aIQ-9_S$N@4-)8-1Q)Z3Nn5aT{gSb5F}jRu+Tr*LZjNw0`o^c)H0dUQWBf-WYx!;}80vVGzL-vBn2knh
#|60IDz`N|TS1~By8(tLgZeS-`!x`+iW#TTAo>8}y1^_G+M4bQoBb1gt;ioEGMp)w41(xi6g5i#&|l40C|kfr4?V!Y#G+3ZxkX)85kJuSo&OR3#EHcETJ+33qK
#|d2OYM10kvvG%XhHd2G`iFs+8mV0iVoY9R>9@46|odUhCWIbR?P(FrpdPh*=pi|Wwge&4Hh)%9)TgVpq<y(^)Gik!@czX9mKBaXwYrlU$85;y>QT8lI5Y1Q8?
#|^2rwky0akJL6Qi?>wwrf>Oh+A>?cVQtkvRz#jCX-0F7V&dZt)kdVpY*Ruj<MDYk%Tn$>PXMe!+>pQg}_T(~ej#2i}?4WaG@@FVKGE2b(hl^{2hp{WVg>Ub9>
#|v$%UFEks34VqgOph4m0HV*v>DiPb?Z(3r~W>#Uw<-l#^Uz)jqV7F-Aj!bce);7433cG-3N%B0kj3V4PFbHKKs8u;T~>)9zk9Yov}mPuWL;)dJo!fZf`pUa`x
#|Uj<WmfHKdRrExc6@*BNstf)IrpXYa-3c8%-kc|fqsdo1P{oR`m%E#7V_irMS70!@oIgE6=Ib5cO$c?FVwVhRe1YE#R5=sN$M%=(k`|eW@_GSrS8L&8_7GpIK
#|?CQ>pKnF~mWXoD<X#l+lpKFUp>P^;<vYxp&?H6Y^(j@elJ9%9xC>sPl(b6n9D`_)K>85bCrFXU*_#5yT_nb^{i>Q#XP1BIUq;>m)@q<#H1Jq_)RaInVaK)zI
#|8u*@K3=IT1;{EG0($zPed!OBF(GHVP%A@QAI?eVF9d$WJD%dI7mgli7{&ZD(Y@}&ZQH-fZ9*>TC!yG=Uji+hYJP6z}I+|6)(gm1Ye5U<ydDSBh_End+JdwZV
#|8LFrY0sDxYbdJ-T+twfKvtJ3aJpw_G>pQyM!SB|)91%L6beJeU1`?{cKF>uYX3$cIS4e&W=HA1GfIHfaiIhoMTYpAaRm%cCPx4LkV8u8q_Ca#C2J=%}?MZC}
#|x<4^=y9(QKW$==EQ>*EhZ?Hgn9{jNPT=W6i6H=--m03=^f}%rz&O<I*)7$&Dj^j4wA)S$B-d{SQDYP3DyW@x0C&~aj2yNme>0)qVJP9-w;Z~K)%zDB;4<$V8
#|gjUUq_#cYKjheari$c~Xlh+li%HDvW2=T!cp9NXwDFUK<zbF;vKE>-q4&We|8B?ud=x`!hqueLFyt%3+xo4^EBK%Im9^>&30!R*aE<T1;?*8R=EFi0uS$V^3
#|-)mMzdp~|t<)kcmryqG{X+Ih4b3h>ri_CoVkahsc?^0gN=))B)f|3$_uj-?(tf@oWGxSy}guNm3k36%MeD+&xY#7Id)kRg;-=vyygf;x%KsN0-xMx^YL*{#X
#|29;YVgeh8A8QVhKA`m$1xV20D^#pnfFZ*fACO&%td}gQQT6{KyHqO2?L&6Y}1Nj;KQos%~GM$`6*3)VbYSL$ZT(fj(xzs%HB#7nDX)gxDH#h$_%FEcm`mBCe
#|tof^lq7JUjALq_p-t`8{S679@%_qGf@lC7XE}~xwo2~k9D=EWn4OSd>R)+0thuM&zMvfjrPZ}II`(~mJjjtO|fENwWlPxfwZgceIz_Y&j;ILK|jY53pzg-FP
#|oY#xs#`uShW=Gajr$hot9s9!jsdIRat=rzXiKbz(){{WWDmt2*o3M9oV3JOn4J~ZBpTTq_W~Z&8`xxXy5f&;HK@px|xZR1?W&OA|wWB(?A{NboeB72j+=cID
#|nAShF#p;sQ<pAdKk-Js%11_9H_C=Fgmsu6ArV^v5a5~_x8lQSJy*J-HB1~~A7Px3s8!@KvkWK+juPLOSn-~r<K-Bk1_4rL+)Nl#9e_-LhwBzxfDl-M4bX-)@
#|A8UR-sI1S_etVLGFyR3;bwx6!!0aT`-Q3+shAfHo>HtXin1vFc*F{U<YDnt#f{vyB_>H?WB|idu%=6{m<0U@ADe_0MI3I~1=C=qVps&&bw>lIYeK4<5@*Ac!
#|$S^pdc)2~<hCz$tY}>MfDtca_wPANMou7f0S)4=cpGnY8`wN3EFXgAC6m|I`OVn1&i07T)9#YlF39`lDrHOzoZTzp$14gV+i6hdw_7PPDw?)`ZvQ4s6y6BtD
#|w=h#p?<7J>&^Tf<1_Ulz(KMoe?~~0H#jM00IHI|(B|fijV3pE&v(+bDau}@@`SGlHh<A(7%!=gbF;dcMnCZ5pPi7$rluU!qt`zIPxQ0%t3JFHuL2)Cw<S&s6
#|4wnim7!VI|bg+&Q-Hq~(?mZ%*aYQyw-XEc49cf-uwT`|W1!$qJy^wb<%Xs~JIRiJdLJ<J(bY>tq*!*{r_Ev_9+DIbz^9(%6`0CJwMQ7LXdOpk)K+V3@@ug_W
#|QRt4mYPjOo#5Gf);#}G`Sm)1mVT=<^?}E@cVQj#Ls8?CiCjxxzL%kdY-}*AJ;5rWKUXy$sF=?C~7H`V4_U;kiExK1U=>WZ-t)k|stf^3I%re~omnX4-PluHF
#|5V-fBR0B36Ix_yUEVKHP?)2h#YO~4o2XfYSIru_&+U{&;BaCfw0e1c16cMF)b)i)XK<dC`QX=Hu4k}Tsc{$?u6eoz8{{DnfU{T3<DPWhjqlJyMLL)*69A-__
#|9W24!Ksd*z$0&>m>@IobeAh|G7MROKD#bM-I5n2ZQZ<>n7h7OLv;J*52WP_IYw6gVmj9qhnm+Hjl?Z^0i(PQrj)qB4VQW><uYI65DvL@SxYHpf`hJ-HjDw!q
#|;L?4D*f^0_V-}oWL(4?k`>Cn?$WnF_I6mfs`91Ar+mqm?nM?=PXKO51AN#NZZ~XtXtVjfujA&*M@S(tRB}IMgWlbJOh<<-FvjOGQvU3Cx@wNCP!GdDJ#0mz)
#|aFRM=X-mr42!!|&ZvPRRuP-7YT3ss6jJd#4jGU$bZ-=jH3BS6;_zWmJOq=lK00LWv_U;L-4R<g~!VQ;KkVeIN^Zhb9vLg!spQ^B$AI6tX^ye03t<`-lK8}^T
#|)k5lh!m41w44{p$YeNRxQ_`6c8&+bxs=ge(fuxC|4<0O?jVyTS&W_kMN^P!fekz4^Op=%0+<}z6g=YnG!jH01mG%sbG*uIfB4g(J1k@TMf;))RCF4(c4kB<S
#|jSY^!FACH#R69Gbh{egOn`kS>H%(*dB?7SdrXR*qfoo_iyZ<LpbyV@M-tPdlIx1!P_QxmXb1%Ko-t+=_yMvuYqa<TxtkwN4;Z>ea-!7+Bp1%6*FhNgSRVKqi
#|>Hfm2Ef-H;>2#hMQG(cBW{rtCO4qkOX%rk#Jjuwg0m>KADHN1!gmZ?W_%~E8+YM#H#jwulTSTFg$-QQQ4oU{5;tQZ-@Z7gII%{q+R&2i590IgVkmaD|wp0fp
#|2e=5a0({m>m7<?oW}&p|rCyGh7{AEbDQ1qyrxi6Y7j}|L+FPQVJ%Uk%_15G^2EWWe;uPr9^m)o<6Kit&Miw$dk_YMH1yIf?t71Q^T-nx?*H6u`{RKJ?Y%65e
#|U!xCOVR~F9I3U{SD48{!fmIP-&k=+S2N{-r)SYc_!sXsnI*%xMTMZxo!TscdSD9lr6o*}NZx{?m;RY^W{WQFdQTZxhiSQ$FcrmZUCY)5Iti#*WT+lA!9{r-@
#|$zgX4;mZ2$8xbb#*S>6W$*vbhV7+@&tx8tv@hsF&+4!%quxTV~tT2(irKUb9P5mrk=W1kz-J82dv8E=w@jW-YM)>}zoyi;nK>WIlsAc3U>e&?r0bmFv0L2B?
#|5E3cX+;HL|naXp)i_3ZzkB@+@<bPu09fp0sW1hlzZ<O~gw~e$umb>2vX%9Yk^2JT2x1x0l7l4(kV6g?*AVbIY7U0PT%a(=3bisfR>d@5sPp5Q7GJx*$pZF~$
#|fe^s>biZEQp64)|e0lBo1`jtV<y;N}!|BO<YzxoUFEMFb>uKliCZI`kNt$V=z|Mpr=B90b#j0X6w8%n68}bWsX6A`SgOSRGbyqa3N2?d;sKiLoDi>X~*u}bV
#|%LFOq%fG;cS}hY~R=puCY$&6BDnUP<!zjq3cYdWLu<zoszH5U^5zUVox2Hle)Z0}7le(k&#^0F0#nNOIjv<Gqevc(I)=z>l9NBXnt$&{?-Tc`Ilf0%EHgN$z
#|O@8SQbm8$7bCNsJls4(6_#p$jM1Ee?3G@#lT>#4|HVQZ!jhMEyY0OHUj8EL*GNTx-t4#>+)EH<Ba>b(ffY$;D+xhCa1SKSH#K+X1|Ib2AIGid+I$-RvKHIkt
#|iOboivrL~VG&|TL>e~s3f=3nms4z`_*JS?(*ccTF54etHSxV@4-f@`8`e;%&+6PnI#|`q62Pj`TT#fCV5h>j5bk`0%(Q5w$nqJnsbq$GN_<_0$NTvZAvhr~B
#|>ufhhH>XFwjCrQHFezWdsRD%EWpn3<LUX^+*Higpgxn=m3d9WX?|aHkM!uO$!X45fbq{LE+qsH0Ed8uR<2{X70MUf3BhVLpYV?FHWm2$MKfTD5K3SMW?XJ>|
#|MEZa7YE9~cl1*_c)S<axLCeCOef1?G9sP9iBgN<R&(*($Z#5I?RrA(rkA~3~dbQ$6ocg%V{8E+Mklm`YR4jMs1kL#g{-{NZvffhmqV|tOX1!}5qbUmI_2gYc
#|Kmb$WJ^0mz%IQz9%ah%gYH@(j*)g_?I?5h{yZLpXon%oOA8y$J_}GEC8&C@{sAcg^BPV>_K~4hKZznr!SgQbzntOw4PG*x|>qKVmRR6I}|5Z9)L^yOxHg<Ix
#|%q82Yt4!2pu(%-d^g@4*g*h`<<r!eyl;G(Hv<A@cwHE)XTI0a~9s+X{N?;y<^O4S&ea*Gp`Y5!iPeH%B^m8CB=X3l^z~jjDEsDPPp5^uc^HFEjn`q9GtekCh
#|DG@e4fpMBCEYzAXFMG7jwNqpa{9D~ZsE}|Hi})@Gt@;frv)k|i{05O(iu$efr>Fc|vbEF!;}UXxI)h;?TzAtSnuVOunqWq%an~tI>BbHqnd!t1z+Y%Jk*2#T
#|zlpg%_8U^tu$tm#IcdUwZ8YQ-_w~MeV<VyEPF+@O?wZj1i6LQ^iV#;jMI8%%&`+$&5-A&=*n+^ichab9RLr&kVuc^BpLyTa2i#Kg!-mN_pTW!|m?R~ege?O*
#|CJv_7m*U~wG2jkd;$t1n9-n!C&an%1A9$c&N(9mS;bR%)cNAS3_8z8U!^P6UPur!l_)L*h42GIrexf-UVV2D2K%1WJ6gCSmN1g_W-*606lbv$uU!zON;YAiO
#||M3HT^ORsJ@yR5~#j5^6bjB>@*#IU4@MOV)2gv5i-DAUhhQM`ZJ+s>6L+&_7aKd71R>YNrBF@jbN|q`<%$=f5oh1uKU5<C0RrhkTOtA!H3+mgqdq}0IDxeS8
#|+}3A(B-unf7-EJy7M<1qz{!3clOt@g4tKUAR;oJwB9*d~hj#j=z)3A$j_8hyDHtti@bCsTkKMyD`@3BH&c%=%*SEu{V#h$va6>GEIj^<;i>y^TU0Wu7C~6!U
#|Iqcsedz+RnC)-Veo-S)>)XD~;1WVgflM{uY+s_T-@#e)RVd6XjOp7$s?#I9j;a$r+u$0<x1QPyEocanS50j0!;6)~uvmvwDvI#_V3N-T)5*2}EumkE#>me~^
#|Whg>5RN96r{70%$4DVnNA`2^iZ=SQNPL8hZlNrCxXX;u3Ws!BI8bARO@+d9L``;Hc9$NTNLK`Dft0rgl&%SCIy(Ok~BdIY>QZGYTzk#s66XP#%K%?-xf}^l1
#|@W5a5Lh>bYwfhV)tV>_Flhx9!+Cw;bfC&pHqZO95S_{|i(=j@*X6%#$SJ#|>gwwU0+U(0k%u$f`CwRfzERl5G*!ZM(sP3`{2X@j(qW0XLJxuIwlLo3q@rba~
#|dVZb-#f3kq6U#cMoh(+}<i~`%3puxzhVO57iNLf99}W$jX}HIME~bC|V!x%lxD^vRKBY11YsSDP9o<9l;j#rkn_p6KNIXkB10iHSso&z!82i}83hRCe1Wke%
#|uDJQ2KZ3vt3j-J9as>-(!Ud9<FvFdgbSRd~r!-9B)wjt8%>z-Y_H#M7V}s`IgP=U!#b6}n1>vBvr)W{!G<>HdsRv)2Ul=y#Uh@i4dXuDjhtHtQLZSSsBRzO>
#|f;1LyzL%jnXp#Zy>K1=tMiGw`zMEe89bO0X>a1cfKJ;p?Exb}lhvtDXW_O8@D>syo1`TmG(ai|+!#R?1bc|xjY06`X5jH_eqaYl;r3$-Y6SD7sMUp2ER684Q
#|@^R1uFU<&7Io@rNVbTrJ_GHiy64u{whDOR>;QKLsw<Nx6(6^sxwuMM<T2jqBS*H+W#xxRsuA&)zx=4kPBNCiCG?4J$8inhLkL46czrs45A{@)heX&;;cbLEC
#|%|SOm{i<n|^bcKL?t_stXcRmYOK4`7Tg*KGp2>Y)@(5<slJ^CE8~u5`iE<~mYdc$MC6WUR4>X6hh(*34G2%=u$%9FqERCm(`gZIl+I}pm)WQ`vBBqT?zG95Y
#|?!%eN+e^;apL;2@bPXL%Rut~x%(UVwGx(kxaA^Xblgmx@C}uq5qei;v5o31U`1q_WEn`ESBA$`7Vs?$#fwA*yv7&vgv<4WEdg{M_rDvnQ^gQR-6C)6GY1oIr
#|Die?elH2+GrR^AFhA52Ka+RZ#a3MA<7(C_%AF?L-55(DohJR*k9aAgzs@c#V<|qdj8jkK8_HSu4rxW3FGW3j`Rf{A94rbKZX~q44*c0smyCLNO0^Tqw1Sa|b
#|erjsR;Iif_<94G#k+N@~*7|rSm%7N!Hxvq4h#uVYS$JgxV@OUzWX7Q~fJvi;yfoWNCgHWBMtfw{!x9_g&Z1oCB%Icaf&#Rs%d&~X@qzSJ0OXFze-I{^dp(gh
#|RlwkqF&p<-Rhzel*g5?J$f4qV^{We;6CiK<EUf&HL1{hUmh~pgviE<AwQ7EMCeeY)C8&~1pebqiDR^PLa4hSkWtN@Bq6w0EHAwIzdZ=v%Jvx>3_L3(MyMSgg
#|C>2@uaLtsNnY$Qt$e=^N3K)BJUO^OIm+o^|vCmbYv0}E&^aD*$9Ju0Al2g}qS`SR{PQjf2Jy<Kpouri}tKrkC7K{0`2q*d;FajkV11)L#jHR`I#UmUVqwp;(
#|$C?hOm*O23XN_APyMVi*E2>EPmvkjX#pOOwi~V0Je8&I`Cy6VG@yWj@+1DyM4&IxL2{O=?6+0K7)l93<7CP&Jp)cL6V)1ZFE5c6B7!kEVzcD@klG3#Utf1e_
#|98H;s`xA}767O2?mO`~e<rp5uoc~sDucwf5Tnbc8qpmyqg?g!Y6L`lRLrqjm7p)kYl!)yC#_ZEw=x%K%Nde5j3{t>dC_YH(^g-t<^@b-H!|8}bH+E|QuP-mx
#|lB!qyq8u!1sfj)jkVgTO(@`j0O(OoE>k%5B(78Ap{^j+E2Q{LD9@64b$rN*!?TwdFiEK0y^gE*pdi2eh!&T1#46(4fn*Mq23KSr&LhF$Lb5`<jcdT;AZ?zCN
#|tl)VC6hh&FngTte8v=q6{b$|&<@2Eij=tHc2<k|~R1(=U-*lf=Owzqo|IsqLZ;wa@wVwCbNtqV7`un3DbTiu4vGtmTo7lR#3OBkMZr5l)ly-_Xcc><lO%^Yy
#|gv+etBqIl?OhGKA^m|+a_(-PTP7uCQbSm3{E<B{Gq^O%5r!?tB*6p>KS93hp{~WN|EgSM_Kh{&by~-EzZZ45SdV^u0I`-Yth_0|X5Z#x9K-S34-%2OmB7#)p
#|lw5@sc5iQBYhKg1bt<6Abwj<85T4%>f4BHD7Pw=-fl8=C_k85oY$zPQlau1Izu?Q`^VebF@G1~oYoNv_#nqy5K43?(LMm#X&8!h;8DKt)NolEB><7QmqohXv
#|6%ruN2>YqPN07_~O`~5-A~GDoZP>0YLxGrZDrTowP<jE~N69NGU&D>b({xK2OPzrrSSq^crs-k$C(ecwcCvYY*SHhtodrorhR^nBUZB~(VrY25fD<*$YH=_T
#|(T&5tml2NyvlcB8UM-R-G1~_W!f1-!ef17Tyj|eUCD+F_u)xj96JkSA`;=8gmU|OF)b^o``fT@yiT-zB209k+WU?c3(YMgwd+ha`{CLF>M5ZVBoS8+Nv)ip@
#|U)RO1&#jO?B9^o;?g$!w)ulq2wTYYr^3?G#I=3TX;a6wT0ZV(ye;p6amSe8Oc6q%>EKr0hSPZ?<Y1Fh3$O^5Isu9>Avw@_hp;2)$*P~H<8Rr>T*c>Sepw-kS
#|ZE5^H&*rVgxtGqt;G7781jFo8&^<IjQ%f^6+9zT-GX18l{<jGMjjeFD-2!CEj^+xz1rxP8Ax?WM3)0wEg9QX<LYsd#N|6_rt?6TP*G0<;Bh4cMj#>|Z5o?t!
#|(;gaX(ufB6=%IFMb~Sn$h#jt+OI5$Qdx$^xM1)swZHjHyDppvh6=k)f@c?EX>{7SYKUAPkhBV!-P@jN<F61gkCa(XQyla0oe5IdDE_mf3(mKL)2@k*CZ$6Xq
#|Hn&NtH74l95MgO-^*daqJ-sUmG+0xp@IN8dw;m2cUAsfI<?w1Aznm%3&o!eF3g8dG#v&FKJv967$s*MtHX=`j$;mUzta2FV)&Q}5j(+OC371sQ@JTx<ddGI>
#|=*+D9>4cm9>{qm`Do#SHOmK=%=N1sD26$fX!`)Iwj*yzbES3xq!!EtT+{!E~!!z7cd*c-@w5t_U<}5hy#YQoG_DmE{e#mXbKrp|h{rj{1Br4m)k+69_vf5io
#|<!)2@!ebdY(Z>@EaCWs5p`%-^_NTF&`?yZVCy>OX@#43x4V}w;ur<DAX7jPZOi?h|!jtN;vB<4Ie}LAm8(_V-X_TwEgJ0chT9d510^LQhAJt|Ng3Gh3I;^lZ
#|ca%^Sw%6m8Gjt<&Uf;E`uv04*pMne6mhWCjaScE~+wCW~3HWzYzleJ_jXdNqH`uX%Q}mvQ%Q`Ipzq51#4p(t{QrTjTzmk2+*B7FiAFKkY0F27HzgB33V=qrM
#|afHzkuHVdSh;+@r1HCt|5m{R4BHHzN0<QIZuem6D&~tjLzg{E{4M)pB8r+R56}?+cbl#F3&9t*wHsRF7W=?K3{~~Li4@5^niG`6g!4~*=Uwz_|Tc2sdli#Bx
#|m0sr3faP8KA&=9`%?So?lvBFB4?9bSNu8LUr-IkLXEc1e2_E5IxfW#MEz5~B{_o)gSv4b}P5dlUwcQ~IYf`R2=3LWw^4QMTNC@6}^$_b;H$l?rKp1f6Owo_x
#|i*dZV0x_dEaW4y}^w)$d+^&{kO=P9CSM@H2bvcu(p?C9d>X97v@R;`8FT}hZzVq-TJUwv>!%5ZG1{&OFv7DYoQa6s6iB(D|<Ly%D*RhY-cSVk7bHI8x^Q~qw
#|)58`F>HK@%aTkfj^q4*UPLE=-SNeAp-Yy*%*;vOy9L$lEus>%2oTi!atbgHOiboHwF&A#P!8M&Pi#-_$bDP={kdAKfXUZjVTtlkBvsIE4%T7ssF~$J8N5d2g
#|7oFbtG|ydJ{)(?8&7JQVIG0RFd&Mt-=djSU!)})Pif_w$`}fivyBPk0k{Tgk@h!-92dVH-s>n-#5{mai3{gf#dxGA?SK5%|U@GwPEBihe+|h-Mf8mMw`^}x!
#|Gx#XuFUv=J0)NR+fdc8(5E#c9W<X^2y%Q&pR=b@c$^`M;k%XOzh7EpJW{V*3oKIjJJKG=uUx@=?uB|}!QCPgzSV=3y4=R2=bLiGpqDQbEESt(^JcJ;k<>PnK
#|c{Qjo$Jh{|CAPw??j9{^OGUZ1u*A2Q(oF&5ojp7_&Q4)W|13yL)`~e|<9!gdd_0HBjp*dYjRP^EB>V}{V59*B%i-*G^wAkS>_nxN&#5;37rG(bX5$@Z`g1wa
#|SDa~~nlO0;hC;9|Goq(jGF3?FDwZG%Ndza3RT5Mb8GV$tS#nQ7vi)^T2G8oG5R@z2&QX;kAQ_C{wJJ~Z4fn<HXdh_K*1@1~J8~Nt0G^eB%kl8$g&@G#akyE#
#|Kq821{$##j1v2{;nw!mYIEUoXFO|3=TEF;aC(POpA6mKt5kXL$C^T@xdWda%a&s7>C=`Sn?i!>c{xy7-qghBkS;NHC#7X?V%bBBYAkujQvW571xUbEg71a#)
#|Nt_&*y`p_uZ4zgYVW}Ja+*Fgp@0^8)dG<ZQm*UB&4I7$8L{w#(hawiTstdVmY^o&{jbSU633C9Cx$8|gi)SM24&@Z^bKH0}_LuKuze*-=;4zqQ1irZ6;+%sf
#|O!FHN<_KHS<>sk{D?#(}!*&^>_<&&?Y8sIogVQ+e-0zk%(``9NRiShl<%Wqa^~7eY{ykzQCDbvf4bhjRu>NKLj4!br<&zq|t<X<wAv4P&b{<<p_~6VHmF)`n
#|RPp44yU{_-Sj+JPSN9Ys)8w&nOVBUp?WkKk0`kcw<VQCCewu*2qps6*hk4dEq939516uG4w~#4`f$n7HlIi2&0oZ=p!2RoFrTFSpsG}PZ{VZ-kc1L$wT1`O>
#|-S4j?40ANSw~{f&ddTW<e;9{;<;#l-s*%S`Pt7wifCyOc-((_Gzidb0Hif2eC^}Le>y(!ucILT9Lna0VN4@{d-R^l)z_s(CVv<<oEmpflr|g1DDWt88u^Dn<
#|KvosR^YX0c@8+$V1%h-MEgY4H92{q8n~VCAFC@RNFN=5%e83jrDv8JHZf-?mPqV_Yqv}C`_4mk23pOC#NgJ)uN3esE9oI>$6(Nm|XjkuODY7ZYKG`{BzbFcl
#|HEMJ!R`y1x=F)GzYd_U(7R?Nq49igZZd2<0!NAi>&?#@ggeWiookggLf4C<Uytc3M$sA`lxf1TuFp+y|K;XHhoFxr(8S|P+vsG;WxE%uFs`VqMQeYv*Gsz*%
#|9-*R~>w{;qk`L~i7HoD*r$$aw4RSnUK$}A(h{N-Lwk4FxOz8SDVSDlY8e8l8^ziy^XOVGsoW-{|fC>?7F;*pBx%dvY6C#0UR~hc}t)B8XI|^WhO;ZnZe&Q_r
#|DJ1@hx~)ed-}@`yqaW4hAMKUDGo!f~mNz{22JWZUpQMy1B+H^Dw|2%S52Fmz*gqa!!M9jrsa9*xBS9Y!rYCoKB{ICuL3z%~Unr9@461U0&tgrOL{L3|!iqg}
#|mezTE8COcxOiRcIFM>Af@}(kDyoH>XVmBsHLu5=EvlCC;B>4+@H%R*sbLFV8D;DvQ=7{nLol)-Iv<-h)+@nxsxCt*Z`h8uy4wZ@eJ-|`SwN33FD?Kh=xtFf_
#|2seFuF(GHqEJ80xFCWOQa)dZ=5qL(*OcP8@if;IoprzK`>?ZBjp-?B;@LW|v&Kb84DGFMoItTlrWkbdoS0h}o5JYbhIGA*7poChXrA&vtUYItFLlse4qNYp}
#|l*1SX;p%RJeQ|lxYfP@#l)-u4WB2RZ_#bhq9$KO46+8S}RQqluoXG8>jZ|}-JDqBFZ`@Xk3;KpxuMy0O_FUQd#CmiS%|{o+*#536U#|T|RJZv=-QP0xR9x%b
#|v6i{k{h8NeOn}A+j6d%gC$9l?^sth$mjFqc85PGJWmxwVq^ZiLkXx~^UJ?WehGJfrXQk$8-j@t|Tv@_AKQ9XVq<XB&UW8d6cLc0H9B6nkV&8(+Ix!(^ihwp_
#|?~e>fT41}pHaIyAXoa9~6Gp;(TcNs^&y}5vu1j}o-q=_RsZTl8tJ30s>obD8z8RxjmtyHh#l3ByD=tE=j`IT?_B8~wtrwpT-@5eyp#@*1C~z+)TiCK}>1t08
#|{uy=RfS?Q~-56#q9abwDMZX{>)um7}oyI=5=}nvM|7Nt+ej;v*Tuq#&a=oF;fenT7Qtc@w+I|(?iXCZ@K0Wl5)D{@dP^4#;CSVqmA!>dBbXlBk-}g&hD;7?u
#|=}k@U#$vK$1L$yuX7fyaqw?G7&r<=!T+F^pNXCEa4=cEFI*_+?Xp|KfHbAYYsnpp32ws9%NKl3(pk@%rGa*x{m<FBRX18W4>%l%=6f+|bR1Su4x@<+k2N*}z
#|`NXL^`qoHhRY9X=pTy&$qGsV1tgOi|`<r;BDk*(3`C#;xFf{ygBAN>eMb$e&pv_Ly76L0i@!%@y_HtURy@qtYd=u>KX41BSb-~)oZtuR!w&mq7=NH9W?OCc!
#|wGJ8Atkqjs@@b7aT{UP!OC{)402xTy?z)uO<@*U!KblY?Lxxr;RHRvZt2g!2XYhWM-B#Q)S|GZ|`tC0O5NZIr0Gc<x1^PS58j(U?YiJOOdis|AR2_$|+U`b9
#|X2|H^N_7-aQ)}yrn5PKb7#ujNft&1zW?`(AZD)sXiAE_NR7e&IUcyM=+S5X*Kxq8;<jdatt^T^tAl;1Dd$UAqc1`dkU|w&8LL-xcUdSfIj9cli?S3{Ga01ii
#|v&Q~yj?-ul<?&G*dFdlRe9|J3AYB?aeQ#g3Xkgkv?&s|~K^@)&WlSzD3^+70pqBOj@2jpiCxmIjLVbZlW%1jOT|g5WC1qVzgfr_rIL}d?Aw{2+zsC_IZZj)a
#|`ApfYOFUAHSxBjzSFLq0C!LZa1lNV(*5<Frf|5T}g<=wegY(pWwq|)$W?7-0ykyy|MWHTNFy3>XJlc#KEvI#w``f@odI0_im~}S|W<0%LRT{a2bkUNnI%QVI
#|Hgv~mIVf`310xaWIo;*AVSJSsUh6Gf1x|6L=%##dv`fD!=-FM^0>}7<2dw$_<^ye&uDglJ)8Vw()bdA^NlY&`Z#m6a{~){P*z>gJauOfg>u7m}bjl@(l_ZQ1
#|PJf|$akcu^=E$TWSBE?o;-`J+EI~DPeAZ>lM(n`$ol8z-#;skvRJ@*sP4Izcx9DCz^WT42EE6L+hi=-+vBjSLGMxIJJ*vw>@zQx9p+Q73tk<*#U~IgJiMw;S
#|P_^A1`x+Tp|EGVwUg2r!;{kZ}Pw4CRoA!+4N5ekL6klq6QRSK37>uR1h+1URvpSLa(&0a+6w_L^gfi@1eE_rNFd)0FhHe%64D|98{G7;#sJd9FeWfuQziQ+u
#|jKY9!QHDANKROR#u7O9-taV<p0uyOno8UysF3v0d7WKe@_{gJ_ZvI+{<-KWal3vi#lsea4&ewL;dwMJdHt-Xmi9Tp1^amDOvA|J85;uG(@w+XBe@E9>)}Ywx
#|%t5qw9$a@CNzw+N|BD7wf5r@#!FrNQ2l+R_CnOM}y#bzshE_{yN_{FGXANCGi(A(X!b!G?lKvPCF?%JdF^tarnNlsY^*#j!l!@Ae9%HU$#VW?tj%wxb(b>Te
#|yw((@kM%7t_%ovCp3ZLM#mR3{ExO9YPB1XZqwxe-)8PMlU@+~J;+?pfOkxGan4eu<uAMJ$9EE(u<YyeeAa35n{1mGRTN~#6l#urw#{5x%OyDZzlyYUdlbuwJ
#|T2nKmd;a%28D6iKc5FBzS9V2mkVwulwAX5QRSvB;7tE3PhYEnsLgUdIXm}M_CEK7T3lL(Vc{Ewol!+iCr%M>T-BbRXwLLBzRBHgEQBpd8Ev;8Ebb5lF`!GQe
#|l=)V2>FPStfdm45o~-+)8$S=uzAp80(nksF?s+xtux>*=5BYspv0)}oc;2<Z1HzLAiW*6a>Zn?>M5465l{<|GNaio7y#>#9OyU5pg(VB7>F*n>)jBX6s)v--
#|NSP@qkFfFW3S)ekD82RN@rW2GmQYH<!Va1?tVF<A{^Kgu!(p1&3WpMLR8}+^PW|~j<;CNdt5;e-yh;0klo;&;WH*wf_@j=gEQZr3r6%Vxcln?-`bL?|Tallc
#|X>V~<<E|RXw3T&)ZSsC+U_ooHpLA_!Wo@HbaRrZR52l2p$MYd}eM*fwf(Uf!G*iUdK8e*P&Xl!0kV-_Sn2{c(uBf2mK2C<*rdA&`&X)H+onTy)yaugC@6qG8
#|J6bS9Mfk2<JYbj2#NmR#L_o{DtLf`cAM{`Q>OgSA*Bl(u1e4Zq&*oQ)N0}k_;x}US?dI?3PkE2BTkJ?5xl#NK%ooIC9StR7xZy{MS1Zv1bfpJM=b3JAZJKuW
#|CXzF60`TdDWN=P{ImfXr5ZzxcH`yl79*L=DevK9$P<9uUa9PdW!oJ4&0|xp2;e<ykdc<=GUSZiCP3+}$x6+?wvSe83Yrdp@$b96;BWNB*sM&o94HK78X;>Aa
#|;?vhQG$V}MHGZe{-(7+ue%3NHRlPtzO%Lt4skyIyK^DV%>_&Mb(rF@d_?CP6J#n<$^TF#OgX}7iKJzEOID7aJmu`}L9^S6VbNQ*mawX~fd@kjYV|2Kv;q6h_
#|-ujSa;7g{G;pqY1E-E_q^fQbjDwcDDa1|<73Pe%a3jM!xYj1Q+22CaYGOjL*I4nnk`EG@<6EHUXe*spQdu#CS?^;-L1XzT*OPat_?{;q=CY|`PVLfVk@LY~y
#|5Hli<)EAcf0o6VmVsPxum*6oh1D$@3{hfd1@MUF^1xzSjt;kHfc{pZO$IkZ}n`7Vg8Bjd^d^A9Wi<*dcK-*m}s*_FZmuM5I9?P_#s_f@xF(Hl;@q?6$;y3pi
#|)&^B-%(v8&&!O|q`&fO2mq_C)qC88PxoXJDDH_1%N1@1j*|n{9GHotQ4P(%+jTQkpV0*m}xuyP_sx4vpfd}ryNQr#ovF#*f^T{fm@(WMf6&i(n32D8X&L*f-
#|+#s;r2hB@a2!M}6cBA~<M=VhJ4F{6Fcmam+8x(Dm8Hz{N2Xyj&#!EewggtzJ@jKFnk0#!Ylo&e@z)((3Pny=sN$Be;rOU9R=&{G78+d_`;IM)<pS@SdR_dV>
#|LS<MKFdvyWAKb8dNh_w9xYbyF6tidqmA{K5KP{T2HJroYd##r^`9F7*5DI+<PF_WwnyKokL0(tK;IV9R<tphJ8HFjM#1&>QapareHA}J39}nq1&;e7%T(76-
#|)vevy_iiy!rVf;cMmc3BwrUDFzFfdKMILe}ZkBsX!s$cj0ooBk&LEODb$~M&Ri&&0Rk+ku4@|<=cyMLb4~!fUeEsTp@mgf43lk>Qj;D_G$hy4Csr4QKxsqS;
#|z3}OemvleN6q3kwkK@7Wgnq*-$=KE|Jh-u)2d}R?zaJJblB{OhBIkj^hpzJ9O6jfLP3#%(2Tseb0#wSUMF<^+q|BYf%Mdum{%$%0rW}*jzg7=}aA%x3IfSON
#|Hj6`CrQetLZyuYi9Zw8YwDu=c#d-@5g6N^M!O{jF3oiy5Ms(V{q(b|b%J>>#e+hB>-tNdbC5gs>F=&7^jS&?W0QG05<94B{i6;R2>(Jvbm5~wOE@f!V@QIZU
#|mrOm$<k61WyhYsBV2Y|+fX9Xx$`5A1R3Fgz4Z*D+LJL#4TR67yO*WyQTuIyu?W7?-o#9LuplG6{hJ<+BRR}x;KoymKS}Z!B8Jsp|b`6UiK0z39h9YK13SUK!
#|ggx~mPE6;=)ZAHhmfFDt{J9fQ0JdkeEv);$>;8k3;|dSN^Sv*5!`dL-_*1)5Y03yYWCbzVc1Q-&L;gZG{7q7yEU86EO1&mqG~do+RB~?%`Er56*o22QR`S86
#|H>O%7k!nBFgCiCI;0O!N{PQ54@r;67*cREG4^Rgue)qWO<L3G1cH=g5fs^;-W(8C6CqI5CA3Lv;=_h2v(RA+j(J|$FSjyL@J{J=9D$t|bBLSTmtO=L9saTcy
#|Z-Ts@4OKR)MO*TREo`g+y9_wc@SoKcPI++-{?XDCN)blc?;RrEsl#Rk8dZ)E#k4WhR@#|~Hw=0ek%=^79b`NWtefRmm`lTiHI!H>5peY5XAyDUQg*`wzRh1_
#|Ml=8u@%)aSmV~)vHT)SmI5wpqfLTIyQg$p8MfX?K2f*UQ`hhA{eQVt5!_e;tXaYjF3i#VshgyrsDxA1iRR~h8rV2S@!2-%pVMUipv&Ztqn@6MWdm^8T!mnXC
#|;-5pOZ%T%0=~0cO$;cA}7^UfE2vwFvL=y65DT}>{T9o`uZZ;eTj0CAx61l~P$9XS#ze%7)LvXBcL3baRnm=$6(UlzW@{r{TTY1_Ax-b9PP(pC$r|7KCbM6n|
#|!f_OY8Y!ZYNgy~s>4SyCFn1{E-2#%dS7@O0lW|xyOhnH?hk#gGOu#9>uVnS7b`%HREdT%jr*}!zB1b?q00EMJ+o}TqW})upvBYQl0ssI200dcD
# END v20-close-check-20261106-mobile4
