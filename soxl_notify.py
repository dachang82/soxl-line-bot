# -*- coding: utf-8 -*-
# SOXL v20 スマホ貼付用。既存の soxl_notify.py 全体と置き換えて保存。
# 中身は日足再取得対応版を圧縮して同梱。起動時に展開してそのまま実行します。
# 確認だけ: python soxl_notify.py --check-only
# 元コードを表示: python soxl_notify.py --show-source
# 保存後、Actionsの一覧から Run workflow / main で新規実行してください。
import base64 as _mobile_b64
import hashlib as _mobile_hash
import linecache as _mobile_cache
import lzma as _mobile_lzma
import sys as _mobile_sys

_MOBILE_BUILD = 'v20-fetch-retry-20261105-mobile1'
_MOBILE_PAYLOAD = """
{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;Qg~kG+h7@hynZv*yhg_O-
`2#a}D*q;sGgpSU{mj!bv|(E>auqM7jS{Oqw}x4g2^u5@Uws`aBxN%Uf;7?21dlK!7<H_vye&LTY?>=Qhr|&`TZ(#swg>D#@G4$zlOwK|WHje?UJI%t(y-
K^ZD;@I)taN9|2P5++~<ZqvG@l_iRb3*@Z1c$wspDrjH&o|9jv27Rq9JR)OGitkcdLKfit_GbJzU>1X~BWZsz*$N0CyNHTn-
^=AMlIP#CwUh!IF?Zijw0JYH<B=X#cOpPNtWIPa|G{6yyD2tnbqDMH=GMtkjv}QS>&YQwM^Lp^18f*~r#McyLG8zh-lSycNLb730;B@4p3K*^vd}LRdNGtLo
VW^bE;`1GckrC6K+O1=i&F}p4$ifSp1TM3jB3OL&kr=@A&R>kMLhEF5iB5*Csobq6l-*MEKplGl_`^r%?=jDfGJrEujUxCT-C&BoQ413C-
xmQK%ym{38v(z4$as(ta?8)Vm|VpZ1((+az;&q3n93EUIeO6LLQcYR~^16ME=CUd2!+kFrbc0(w?Kmnu!xB;WqhVn4B0_`Lp2*JC%}bOzzR|FGH^X+|TABn_
p|$wtiY+ZYD0`=y4BleC!Fn)ngBrZ;;gI|2^;TbQRhRBSqnZPUR<aY2sjWltnrSH1`fszoXy#{V!DH33M?wIvUjJT#UPbN6g+E!kvk|lo&p&QfMBYlvU0NVt
mbSO_>L9&a*y414nXXog3<DP7rH}C>OT69}RTa*GCOGMtgK77~`nAZE1KMJdZ@JHyZNN$IZx=JE-<iN#ukhfi%?|AaOAMBF-
zge<P$sbm3*{#h0DKzy<7(_Oq3V>IAxT$-i-8Z8^=|T$2R3$JT#dk74(H+_hec-7|RuxNF<ka8Xlr!!-DuCKM-
SmuZ8Epd4*LJHF$vhH$Gk%Xo)l>5g61K8G(}@eiSEI--4WB^i8S9kMFrvtk`(vEi(jw9#$9ve+>r-9817X1u!(`O!r;S=0(eMu4-
&o&uilS1#h;OIrDCV!Y#Po3HsShVA>W0`$h}0Ht(mdc$mh;c<^Ut;~_9;2oE?LI^PLN0BIh)(bW<+D<X29a6nFrDeGJmFthOdZ$f=v}|ig+J^uq4-
WkHHrAO3cE?W$yHu<@It|%CyMywtGhXZ3UuSD2oCA7+BUj`C6K(h#(DmE&ksNIRE#CG~C{h%aa}hAF)x_X(t}%G5d<5MTnbDs{<gH&}UxxfNor+Mkum?qW_U
UIpVCJr2qAcGAIl<?G&4EX`a!<*iIJ7ViSHrfipg%C-6ic~%$6v|(deI8ldi-n$jY20<-a>XcJHR-
~kUJ`AIQEB&vUjTOl;9y?NWW!i4G&wPNVltKH<AUp=z87^==P5}ctwr_2S?#KA_b7e@3WY%{9(Jb*clS_ekqtx(-
?ji63_$0!J(Qz>KC7iBoNsNv>C1l*8~xycGJJp^ORU(#gRBT4p&8iM*|?J2Kx2z%3HtG1c-K{(gmVjgQwFt&t=)W5qh_|fWdrdYCUCw9_>m5f_<-
Wh^LKHE1DN)2!YkiF{)wJ_!56}M)mm(!qYZXx|wE~7o8=Vhje2>vEIm;?+zGhIZ6*aBmB_=H+~d7z*$K#Mp4{hG!QvO-
B4vpA8%u6(UU0StLS6V9v|l0_>XnfEE`LJ<;A9d_eU^_F&*9ly>@qoFPPZzIv=l=gdg3M+z8{j^GLa2A8P(4(@p;~6L!w$u@qRRApP4O%y`K1P5GRsn-
;z0ZD_*`;XHpy)mMqJ!QE!XpPDBVquPeJ{Go=*RAShy;doWSP0sriAR6g^KHht20O(_Q8M*LLVAZ%GEFkV<A91Q>QM00yAb;^2w7!U{`Vrr5N7rgHZWyCL(N
^^4<XU_v9Gr~8_^5Tm0Y<ZB2gL@soxQZ}px<W0=W@Ojnbi1%2isr*M<>(8s<eGKp)9Ef!Oh(8sm74xlEI+Wf|I-
M{zcFq3pTOnLOyOIBa)Nsj&${Wn(|rIeZE<_(}ZiKQ1u1qow+IDUPxZ_B=@gwqx!u1ET9e7>O2dihgsf>CD5MsL2iuv2JkliWgNlt&9c()*aM+6`w<5ziW(7
c0^5cM1San!o-Vf@=hSqWa`PS<(5KO&`%yMd^0|G<kR#Ld1NKQ(3lslUpdbu*Odydn2Bew~e5L_4tUQIGHN~uIo7r8f9$j@VWDjr~8aKm?m-
dR&N&IR}GISNhZ7Cwl6u4$j7NcyMFIyqOB-XJ6w6A_hzXK)Hzdnb2fQO*VBTIsFP{@gQlPh)0!|V9@Fn3tiTU$cn{!#BU$5sY~zMDGmn|w^ICd|%Fpsma|-
~v@zgX*WyDVG>o&P_(hz08_fS2R3!(3DJqbcA2jTKm-AJURyoDHNr$>2w|>%U6aHRlc)iEWwGQ@Tx~Iwj+;3&Q`6kYS~jt@qnlmZ7Io05&jCka3kMwcZsWQ<
ZjRadT2pN>6te0wm9t_+GPKA`+IlXGr<Mt+75e=RRMb|Uwg13#Ei(exc7ft4ND!I(mXNtU{mFR5)p>Y&@Q!Jptv1!AJTHZ@nyK!KR);tS<3MiVKFW32K6YIa
nEq_Kp1M?#-DxQWE5P=vS4>b-N%s58l<_<A_MRu_%#R>Vb)u`*{3^#$!&$-
XDYxKJqo7ont^4=<Ipt#5GZOuiJl1(mwf$Rt<0@fIB}!7z3v5de@fN^vBtg;575MPF8U58k&HNL|KuE`z7VdH9V+ZzE?AgIQs1a+a64CLWUzhy>lqI#mh&kK
66P>7`jn~Mp;Q^#n|X=Os4tA2RymO9WbsL=CIa^_fkpk2xv8JSw|dXUmOOWyl6*Fr(xINB&Z{+sO~A_VWMbY<mr@W33&X@F_*aqNwmO#YXgud9pH}%WF}Ni+
LtN83xowUHF2Beay-E(dNS$rr-gfk3=gxTQTpchA=`xUuE#<=K9XEo}pmP*Uh}w1*JJ=@$9zVTYAG}MMe){+07I<$FR9B`-
!ZW8ixg6ypFB$m2K5)}fou^Z(!nCW8u;jw|4jqfANuHUJwYE%SDCI70)`aC#?X;qLKeWL<5H!UiV9lotZyK#D4g+H^drptLDnC3*33AA#S_27@o}}xzy-;-
I>|`juCO!+nUZPfD(6jtqeQLQa>*ll|wxqgCR>x;tubILg(WH--
=VIb$bkND2CC26z3rGZHvawc9HNTh)oqU?V(O$RJ!;qS&x%J9Y5=oLq2twOBMd8Bg7K;qG(bE}N{(qy1UAQb+P@ME0Y=@I5?Tx8sRuIu~;#K(X0O8!fQ;8ql
`*2upY$(zwiwQDC_`T|ds9YKNz)YkH^iBpyt%5zD60Fi!4N&IvWB<0Ih5)C%_h+;f>Tn_rB^%#PkA$EK4ZLR^hf*~JmYg{+>R*LQG)zv=lP}1XDp#N+V4tpF
2*f7<Jw8QwFi-
)>JcDx3>9FDotI&5d_(nA2+x=#h`v}Jql+`sWN@hY)nYydhjj0jh52w}$L#ET>_zWXA)3;$5PqCK&C%INtc6x{xlRrm}_)C9yOrnQSPxE9x*ip+ToH@}ki})
3Vd~qACQ8y2xUG{~oaiU=zwqxZ=dT%vxhr^`kvn5Lj;MV12+}l}u)^$XPJ0@M_)BLz;8`<q>p~8)Av4M6;igBBe1V#>3g%ZCXXtQmp(w>IxGzgN0A(Mp9fd&
9<DTL{A`A=w_h~PfI--
%iK9XX?Lsn>u@BaH1>!C0ydBGXCA!~aB73)K^8Jafs3DMRq=Kcu;(8~cM!JJ*n{`toZrPS~&u1N1k$s8JvD4cngxMtvZd0u0e&%w&C~G(#kd&*(PaSlB)UI4
nfF_@LLlI*?X{xXE2+1Sd*xOPrk4FB4U)Sm?H#Lwkpcz}FSU=r$Qef3T1|9W%*ht)!{IP_E%vWX$rC4EaopYNC>~MVD&)djtM)7}75>DiZmeVW}@f^~rXqKN
NK-tBx4TpDp%3DF0WxDCcE8sh09)vT4|#cBJoZVfdID@+$Nt%~Td(=oRQl*=sj80E#W9d)WE(Z*VqN=Es+79Jj7eX*exB&SmDp@QgW?0;~`1@0H#ZOK-
$TU;7!f_{}o(|F$LiKzIM;W3L1pDwxJVQ?4Kg`i@%lKcqX8@LBF{fp{mH8w#NAX2MKT&P^KJ4Z%6t@bgWDG7&(*afGL~u@n!~(87^xinByIolSS<2AtOKS3V
(}z@jsEpd!ObHDMAjgxK#x4LP#h)j%MEC^qa?R%6*{9l|>Q=g4E%?SatnJMLbKW7yf%6o(htOp=f-H)8G3?F3~Loc0)974V2ZV^5-
cKVyL97naBkl#JGiho~JeoPIqC^E48hofwt*L%A-
?G<!+ZEQmdWa@bBe8n(#6&aAw;BXr=(C{M#IjVVwb(>CR9Z3RtDH9I?W&A0MenNEOCG@7rbDi|5A=;HCX^yM{CMnV1?Hejx>#D4X;Bh+)~@XxzktxG+k)^CN
(>Nl4Y?Gsh-sFPfGT{~-SLpFLy8p2m;8S+e$((!$&J6;Z$f_KHOuhcgZMh84k5;gjYDg$j3&Rkf<nG?*g(U*-
*DD^GwrT`$WexpVvh~Q^d<=R_;px{IVW1Rf`#diH14UA5g7Kh6`eCIe+%nQad!?;WbxTzeVY}Uo(+irZ0xVuT~l?UPbrbXftIg#<NICr4bve9ZGhMbp*ZTO4
IX(lI+mF&ThxgffkZX;~Zc&h}w8h^~+hJAcs6`Ap?jZmjQ=6cT;Ed=3W1k()Sl5jU-$Mz%pciT&E`mXbV|InPCmk-WmI|oW82Q4Vn_Jbn-UnVPq(%9(ksJA~
hGr4RDgFy8cIY=oo%z62w(#;{PrxI>lpxqNEW^$&jr~XUg!L{RlQ@q30;(PK$x%sBJv62RW?l3Rgul`;A07NXLFJbB1oA<FArI3ivRPNXGqi{^N7e$?crhU~
d;R<>0{jX+QRL)qI*p0AQ^KLdQGm{O^HVG)-
x3H4oXZ2zhqYmKLME&zjtvs1)pJ&L3KssMhLMVwtb5^5kpYMUY)x!g85vJZc_yK7~Df0V!xX@XUg^Y6PwfX+l*rf&p4;9K-
Bos2J28stf$(gYv9F!_x$$aM&<+sfv?;Ne&QSx>R`vFak;c_LPw7<<<eZt0n^NWc#DB?HZ6*|mv?@b?fsIaI4Htq)r+A6v#cUcSxqYhX&UXrhJ+I8=tOl#|b
M%h7sW9R)Q-kyH;&Fb}MPqsPBQ8bVJ;g8&#U|Qj(`>DIer1@^-8N4YIILx_J2f4|cCfXg1#T`81fY-
*@P?+V}jAK|wuwd<wT6H2pOn3NYS3gd4|Ddm<EW=gkl>TajWr+lJ1wx8|R?1xMoS0hK-
Ki6ueR4{;wZyY~w(qC2$1_)AeI2y}84Z+GX8Rmkzg)GuNH~Zmx!sVp|2ETMHOvE}*R3b(GmBqX1Alq5)_+uB*q-$)*hvb#^>4Si#g&`Hz-mevnf;#5{pnmh{
ZoKH<cvSi{HMxy!IrO8$l?3^U}9-
0mhiSDvO;?Awuo`N!1}r!G5Y?7^~>sk(&A|w{&%u@{BP=t*u3P^no0biQC?K{D>+0L&D0iLEqtkBaX@rrX#w1W#yXSw*RY-?-
vp1Dl8h@#SmXr&B$@sK5H@n?rv8G>-EHyxDv)1Om=fl%sbC_{DXtP)(i|*YvQ33&$#Ct)&Gp2cqeps*6-
})m%dxk*1W_`oC&6+4X#ZuWW0Q!eX9@1phhn=f&%rOT5VImWDJmr=T2JKOVWx!e!c1*}a}IS=ih5@Pf51ch?e7^$Bj(n?sHr8>4bBP^{h-
+fW<|MjZAT9}2AwvBp5`#5RqzDRByC0)w5jrYGjm(5Kran0yl^`LL05#S*WqeR{OcEiWO}WIKZ#JuA7t$W5D!WARpgNg32mwkcC%%{B6VKjh*e&{&I4|<XeF
3pdzBN=-
Dv={M3MpnVbD`YEiZ<kM(b?be@AFvYzTJ=(@E@P*1=GZzI;n~Mk2`v4Wh)>=Ph{DBTwp1B;dYf&M06w^`iBQsES*JM|@BFsTrR!E#y>bM?hPm=~*SQ83=8L(
;BkWL4bEJRjmKA8_uTg5-V!s0k-
*bYS$ltHRkxDWzF!tDfd0y(*$ZXyA@2R@Xksz=WXBMs~e^?{q!>G+R8sqcqSGn_Az=ZR}34FhoTf8lv~1{zEWSaJ!*yJKF_ypsvaw}1qnrL%_p1(4c$gq51L
U#lP9iv)?_CJh>M%`5P=6bdQ}2^cV(3`!F}E{rW$tMG}N3O8qtUJ45$3!kkxQ*J#$1a|D98fU-
>tA?E%6?wRtH)DXL~ER=xy!Zf8D=B$Ay16Py;_uLy@xbk0w~1{blFU(SXq>Cs4I`?<2`E|@gqlc?DKE0d1WkS1Y!9KK(ofmt~P2x~vei{&qwJC5<_VxkAnFZ
Mc&Wen*{d$cboK(*Faf}S_I0tVcnq}Xgk+>s0!HpPmwITKq=8Lglr=G_N^v^@~wde*eGhT*a37bto_<T3zM2YHYT&Xsm&(#RQ_Vhkg&>bFroWbC2e=Z;<Cn5
n=um*pr^ekIq#nlkcq3&y;F14b+8D(mD%L}xEFhg(q#yQRR96IH*$u1O~mGU@15>707@%D5Nus4M94x1cX^n?O!LVgU47pNP^Uc3WEfG5*R@*u$uH=4_|fhP
$<W4SU~y;>*!lo8KiEai*o{aL0$5l1;u;e5y^l{+{D>Fv!+zofm-qF%Rf0ZO|>D(o+~l%Wl<9F!l!-;n_dk?A>e9J9FAsr}ZjYeww0@_Dhn);66ul+l-
R<Q&|H0JwIa9E}a3gD!~zFduMLk#Sb2zKM)hu4lxTyQ4~tGo1iXWwU}J~u>(dfKZslmkmU0$%4qxKBaK9|ZopVbu}_4G*a7o;#XcQZWm=IWPviA};i~3r^Ix
CjU3R}-5|ox1B421k%tvIOJ$jjSwq3S?6WU8P!$n4%1*Z!UD-J-
3s+!jUntC$GgTOMvQiJqGk9^m{O&_2(c<S=aZjWV{&o65mGqru7s>MCv|4j#@eksgirQyXf+E-n_n~JQ+z-
j>MeG){Xe*O{30XsG@I+*3Rk@(8?a=ur>MbEPCyBfH6t>zh49lr)fL+2S<s7EV%FcW|gO#l=*s2r1XOm$W?`3np7O?Lao-
O)ocDo;=0MrR;;$t{*a3@S3}Mx~#;!(JyE@4x`99qc*E?zL7QDv%Wd{{IzER0y%I0DXk>+@Xmt{NftoBCK<TG?EW-
&5qdIs82Yv%BM}yPyTL?t?msf`S`4UWOYx|SFo_{GT$Agdlg~%x5iAM6bOq<pkTFYLwe9e;`_EzrzZa;7?==7fHzvw6q`0&)ea_#F}E>;z@8XoXD>P4%&ww#
Ryo@J>cIs>49|bQ+#C^03ROIH{96nBi%Y3KKk))5?ucpX>lA>~|LWxsu;3ZBK`H4bt3EAEnw?wed){Ofk40uQHFLPUp}Y1u;op(%)_QXkW@?NAC8H4J$HTSf
FKxG73egbxKz9@PTe=ImR2vdz+7!GR5mA<pZ#}M3D4GBo>XVmyZ7pHqf4_*8bd!nYsPD4iXJQ*lu^53+W4J4EP80;@ZnzuMy_-
h+i6g^ZeAo6bsl((g5rIqj739T3d9F7Vg|yU`@mu)Zzvc0WRMu!O1tF_r3*6H16sNFuk4+eowp=wVU#B>MH*!}4#DNRQ&#Xlgjxh4x4u#~m|5rvls`_l2%se
9mZBzy-alqd(+P!QKI|lkrGyBB07QXcfid>8K?+_#;OU%fQZyiKC&?QwfTEpwF0bk@(iXZE6<jDgV^6>qde7wzsd5$>(9Tj#{t3#S9sTM}&{OR&_-
}BTfBe@_xKi#{9`7wWwvUu_SIM>y+_5Tq#eYO|e2|^~!tzFJ>DXh8i&qU?jT&zN}Tryo|4|#^??wp{5a|3QiPC?e#-Ixk4#~n;r(Si_^MtZEff-
@<CbM=FHR5>DvSKDj}*6rP`p%9}tmR2FLBV9Yw#GBVRlnqo#QO{~LAbb}x^R(4eT6A@Q)~i|p1U_r~Z3h^(?4OqM{!4ClbhN<yT|)<rrVe0ByV1zDqDd8@gK
WLr#I-
kp6mEa<=ff#ZZAw`|DOdcviB~Rn*mDXI@J|*A26j%ne7X10eCd)1r$}?N44G$(hlwzEMR;den?Bi_xK#vybXNxDnTL8jbRwyaG#}t`v{SWxhKzPgcVF`@T&*
eJ`hYoumTc<-
;UZbzLUceh_YZwUkwbq~w)k$Y@*5ZKxI~6QZwY_QrQtL}pf8)pf=gIZ+cV;b9XZ_{A0}jqPvKe;NQ_tb|2gkH0%nu!cYU)U=QIgaH$&=|n*x4nJ3Nh<Kb_US
6ZykCI5{0aErBMd#B553gfo1ar*BgZQzbo7s5eYKueF-gWa)2r1IbAn?rBCk2VpuUM*jlVvbXfuS;}>1X>J9D{66O$nR;vb_mC6YBWGlks-
Y@xw77&F@xVF^I!-tGWK=CBhDhMWD9<hKSxiP0H1T$TY?-
{vT%=)cu12b;j~yNSdrt8twRP^qa5rctiF_pIJp|B+LjsRfNpmz(Tby8FkQ9h7a{83<R06mG@6NG(KrKv%i*4^`VSjuZ?}SfxJJ6<JjcL3-
$m6V9?Vn;c`3TYOXbU`@c4oF|DZe9!&bom~mzf9?a;*D)%UJ`T8qKseW&|lO%40_>)XPz)FaW+<+E*nngBC<Tm;QiWGZ-sQDPZ%W<ZV}4sWw^?<;n_(p*&rT
IY9f{)3l)MK^)K(d?_L(glX0m)^>-
f_P)EKJW)(W)0XxDYxfklziZ<9)ZVDj5ZIY|zfXQ6j>r;Q>u;3DWolqpiCp@4%fHxxxA&||H5BXxl)L15{~I5TMa&Z^YbpJz#6<pLyvKzV0th!$g{Vn*ck03
?#tvbSn6Ok}BYV<nFJuYK1Z-wHT&XH#I{bUu_d7((Qp^9hU#11L7x4l3rJ~IM)Ph)AnPgQZMMCe-k)!05uS~;B-xqy-AWnuGWYPcxquVU=ko3jnYOy9r_8N)
kW>UKOsfR&#<pAueOW~8}j1+kAPo_9Bn)#|rKCPi~I85o0t&Tyzid?rmQo2S-
)a`2lja@xCH>319xjg0pXCf6%j}jWnwn=2ER&!#3_$^Si{+h(j3sv!1u`ovDnmePjV^I60yFLEUQ(JY*9Om)=`#UkA&PR}YS_1OJ&Tt&qrou%EJgrO-
QK;@<%JCn*JIW+n%q)43T40NrSt@q>5C^lGF9Gsdw;tK_k5Q6#t##82fw~6$&t^@b(hnYnS{u)yN%dbyqI-YDp3<L-
mPIa0P<I%IkWdgnDe1)Jg4LaM4Qw*zjiXa&9lI~uE0e7;uye}eVc)+wje_T`?a_T;%K)=T=2$pg7b=6o39nr8NZ)<s=Q6ED!gc@U3>Pb26O5s9MI$0K*cJp<
<BddyCu|xKq%EM{v6>Q>-
SgehHbe1#GH2fek3pO)4r#oot=MsxV5NLuGz%|U2QJS%5JhBs>$95Dc|D@#nH(GPz;h|kP&aDrQ#UTY1|fntusc$^2g2uoyE0Bw6Ci9JpwLoj|6cIxNXLNFa
c;q?IrZ-kTzcHYWCdvIw5`)n*Eo$e#gdsV1R9y}>~i3>hSwuK6FSL~kDg)b_~NKAHBzviq$zqLel$2PD=g)Qg>e%n*C$S1M+EFSp5X269F<Ew^;GBm$hS}2=
9D2DSy~K{73LkodNRFKtj7NUtXE3RfcVk@VbWTE7)9E9)Vo*VhFO5b^<Asc)6;T`x5p5|Mza6{(k&`1Ey8<%q#;X*xK8*2$+Kn+eGuFv`ygyo(P1sHG&B?al
&*F<9FjxcBAcx1?Ln;q%Cq!xHf>lDiA){jdXGdH5q+ec@dvg$71fd~>UPUnTiSwCa=-;&r=Bc?jB+~PKN5nG*)GQa7Fwm@$G=;x7l_&=3Hme}8IhYH-M-
y)2BJHz!wbAFYjGC<JNNG(J(LA(d$Wql2bo_8EEFm&E6j`~bV_=&47$54U|lj#LZ#XdQ>t1mr@`-E7Njh1hwodPEy8S{$1(Iem-
V^}LSh=dNNDUNY9@<dPrRr4XD^hu0Lr)UR?rWhasCu~YZ1oE!`P_WyvZs_#YG-DDsWj{$ML3x%8aHFx{`Tc;c){}>Xfh1$p5v^1>&2@3$ffPU~`vx_%d6>gT
{1rySxO6HXXG@J6BR1nS$}CbJb!m{sm^Ww2zkw_*V5;ZVcZNW~%Xe8%n(;MbPCsSW3iTfc8r1WbO-psPn7*FmC#}EjyS{_!52|ZOKDS{h$o`=y!AKKKur;JK
j2x6-
VMWYkH0x6a;YVRF=+C7D+ENcq$!(bs0>VLjR|y<Xq1}0iBRsOm^OmO*W`#dH2D<EoIDf`7?i=6(Tr5>D2X5&>ZFcH9ZW1*yEj!gT0UPNFhE@JQ@BW8@rjr>m
ML!?b$mls(d|Aw<}aSlk)PnrGfCq)b7W)<h|WS4aaDWi)?BIA3IIqi4=v7>oMZrpk$6#KY*mw0BxU5$2!qXiiFU4>*5mkHpd8A@em71u40J#YP)GRqH91oj|
=kT{PeRbS*G=aC-~w!%|Ozp*-
_?UWGF1I$y{}1_4Jb)<@k%s1Q^l|w?M(nYCsyxX6hW0`;sney9{lU6!}ro?{X4nO03%ZT)X)4y&1j!vWeqH7CJxETQjReP0cUXuepTv{3LB;fEZKAUkE%TOK
ffM9XroX<inJDlBmSD13j3OI<XGoUdk&suGjr$c-@d$OzPyxBSmYp3E*03X0oXm+&M9WTWq64F!yT7qoG#Yef>)GocPVToL-
1sQie{D#S+K|6<t^eR0|mU(8P28TQ7{in*c!9l!*G9;_<L)0Ncko4Yi?S`1>8mz-
U4RrM({PZ7yQON)?Q&;a9l>%O{(a+IxrsF2Y2p`F%sjU3+St=xnM0@trWo`LqppsEP?@HA|H)D;}M-
tWHLUhTnWycyOX;3D(Z5giyQS%w)v7{74eUr4s;#fa2IMuN|+=LQg_L3%*6}wj>W6r=noWtG7x3MDaTMU@l7(@9W+knw0RWCqgzE=a4MsRjoT65|gD^wk;YK
RC(qamgx1pwmOyD>I&iQhJUbfE)?do+*uZ|bB<Y043tNJ*}Bz~(=c|2l)?utgGb7raK;Q%GAq}EgI{Ww^v}-
?P@dQSV5ZCiaPPJ@=p#l)_1?PzRp_YwCo!|k3de!l4as1LQz_)CYCrm-j;O`N?CrxOA~>(K@5j~5Mf5vuV+#>?BA=LpkqA7Q<-+vC@4ielyK?k@Oc-
#gdnzz*s<es+W+N0qU(@t0v_k|MElB{V7?&<(Pl2y9S2`Eo(JBXf#2Y~o#+3~=mrTnGy|g(8AzgvLIPcitu#Cf$HKP%t^sKWk!z#$7uH}87{HQW0o&E#**Jj
GF9VLexQ=6NF)%{&Eu^P<TzamP}$o?==J(RZ8mwgw&JCNIrJ0<+^0l_qaW(hGM$H@DpnE=qmuKQw|rHLb*@>v^yg0rp$U8<3eF<Uz2n`Dy~IowCgJ?zX?U?B
kn1V~q3bP{P!HuPCrUm`RHp)(mNieq;xw}Z4D=K0RetI+*AJQlCI4#Z?O+$G_5nBcJ{OllTq$W@j#yu(xLsR-L<Lsm9$i{mvn@t|@Ibr-rPKuEyoSIDp$8y4
t9%T9y*R5K!20%8zVR!(}TNqJZ6hm^;o@)L_;&TkbbOBu+X>)p~iufUe)?hQ$k+-
q1sW1`K9763EcZA!ZHZ#Z`bI*@oa=8aZQ1@pRg+4zXL?o&1`Y(veg7!JCB5oN84^L0<R$aP_*!cb;;ShbW=co*YnZ_5YHE<3uQ2(S7hr7%?*QnbWTW=B#0er
Gf+&1SZ*e;~>2j<|{%EUpD83o%4~^k-&P-xFVB!CexeNwe%pHo-(i%z<Y^{9%^_{Yn-REaV4UKJGtWt%SlxdAD`Opim2}8RM8AopPft?M9OmQ(+9Q^Ml4K?^
B7JjLwROizQhwPq}&1jcs09g>YWk$+tJ*m-NEYQIWmSpBg0^NMg0z7RG%Y4rvtWn;{T9C`9MH37{wTPJHeZC9x2Fi<23MV=wsLLY*npEn2mODt2xSJj{m<6-
k3~no;g8Pi|`)l0!}Q^ik=lV|lSo=Z`75E6<I2uO5B(EI-FI>L`yzyKJ+{Ez?7$IE<!k-
ty}PIvC*QC{}Jvn7?Z7wXGL0&9SU%Jp&QbzjOim_wW&jy=?yEC{rqJxB0cQ{tQ19;TE{I+a+UcY;U;qMt0A9aYP<=fiYFTN)HQ&i83wfvA&Eo(4X-
RIU^K<yXU!hzVg#7yIt{CORM%KZj~)1n=4cl)o6Id<J&9o0w2<6P$O4jsZAaM=>C8SHsnc=R0)r-bTNYjBYaW~V2LK<8e1r;wLqC`_`wdTQ4S-
>eC7**k<}Ld561`S5Z5T-8@fiNp7{vvb*i)ao;Wbz%TM?^x>7-owB=cO`S*O8R7>YT@H@{CFQM*j;?Fn%$UMP6aQimk{l|$(7YQ#=6`X+G%`Xz?-
mVEY^#k>J;=@zCk~Qz<=5sN4xK%Mtq>|<4>UpM@j|&lo^b6(rR2laHR{oKJnVD9uyw(V~l$e9TdsMr;KnkTmmK>_el0{T*ou8P53c_i~?eCc>!1N;fH&Qzdd
)=2x&xZ^ERy~i;R53a*p!CmJfiw?sk(WU%aHXW{v;3?8GS^&EvP&B^>;+U+v-
sZ66V2;JhEMjs<ghk3hrJ2|`H%C|4y*8p19x6OyCQIbi$8Z=Od@nur|B@u|M`0IQO=U}Pwb?^Tb|RG#_%Kll6Yw+(Ln^Pq`^OG>`2*NWX-
C*s|5LDbtWogUtzS7Y<S{0y71gg`Sb)<5V9P`ux3|e*t?GBoep0JKRNz}(J<0u^pp0xFFb*yX%vtXD5m)HE*;$5j7PaG8Mo}Gnshc^$9?<7Zl=w&IcA3wQ>x
n~#6y7>=iRn7OZLK6*$?G4_`#h^7-q<s4X007niHd<_>Dhbf`le4%%Awvt*vh@YYcEnN1YCCD&W>)dR&V$F^kD`Xshgm4H0AV@<3BQ=$o@{-
SaZOG)|SqE;WUOqy*YShE9}uH>P*z{k2Ivp06)^Ifydw#U`RNd+{A###tU~gRti4(_xa8HMLPN@#XRNh~RM!$tg>L8`kfPAA_;U*qWkB7@z-
BMRAM)fNJ~=%V=E@wkURbartqp2Tk5I1C7%{UZ_L^!p)=IL8q;H0X0BezqX1*+OfHn<MathsGE9ts%9~oX_!na?|cd=PCwNBiMkLkJgF6&p6Qp%LoLh#SROc
HBWh~l7F$uBN`PvDoPNoa9bE%9hktYJ$st1PVLZglC?VF2*;$=q7^lA)JREkzZn$t3;6mSXgJ6teeY0$R;v(M1^X$SHLIeAqXrI}EpeGsqk<rtX7XSqML21R
9w>5oZ*X;I`QthPV`U<vLUCOmtirx4sI5-
ATZ{e`AZ4HWiQrv_NGwpht>u;=5o!BfO44Q>4PFw!Id7zuU=RF6n_}&r_x2Ep({k_`0PgYxyl&#a58=l>Qq{2(!mo^_!Th*RCH&0(;qJVBNn~7Wdk-j@-
HgI{}`0v8qSg<hT6`fv;i*Us8oBU(!IWHK_>LFo1^+X%YMMb4=g<Q)tFp6l4bEz)JM0N8z!e?eDzndQ#k)VF;hs4R-
`Tkm3$}9NLh$xPpX=@Gq{fmFHa+3)!LI^VxHg~t!I+|Iqr?0JML3}|mUe71O?J7*8;>}DEzle?>*^=$o&{9Gx$&Q1~FE6IFbssEKVODOB+|aX%MFQL&)?1cX
W9Fu$Y?TblgnMzj5xxct32T9L*wLN>@Lpc~2PQK<ZR%%&m24N;tTS>kLWVL~4sLs{6P91a*#_Mx5n2Esq49*C<0X^Hgfgsixg#SYDF}CSv&GtvMz;aX$(h-
&optC>G{|q;AhdT=g3)BiRAK}&s4w|D(6b>1_PNa>tsG?iyo1R+kuxLV8u_JmPDhoI-
J@`jyu&GMg^aw7%=@=SetwS!307}yYBnux4heyCqoWP8?0hQ|ZCHDiWqkAIqOQZ$gux?{Bv901j?xWhtkd(tlvQFxbuKyRZf6taP{yRhiLEsu(E9%|yla~2Y
o0m^tzRZ+h;KTN<T#}SB)u|%M~M=KxG(-MsZ`-
M^Fd#us=k$*3nE`fXcBuFH`a45blmA<AM+xjM$?l_9H}hCv)as3w;CyJJTHw=Nnw&JMqN)f^PLIo+O<dTxF`3>Sk9dgwVWy0(sg%H!&?)x&MH65G-
D91w7^eBS6B&Lv}K<=!xZJDJ_ft%OZg*uyyYH2j(=^AO>krJ{Cq7<S>~2QR$$G}SI|5N2STk^Lt-dv1{$>bna-amX?q=hO>Z^<T(TgJLJn~bEQVkkbGj^Kq5
J9nmvdIsw#9-cUgPxeSjN!7GNQ&l^VX0TLbqKf$>5GS{fk@lYfIPW%sA^fC<|@)nu*17*33XaKJQM27SNSz(?@c(jtwT)=TL;24MZ6XZ5=-
e@_21EipR(=vPlbP8b_S~6#jy^k6o;+f%0QD76a8l+ZlI+S-$}NtuNP?!7?}5O(Z%}qdQ?L>11ltxcN-tV=U=8E!Oev5)Ad}aBNFg`CF|;LK+OZ@zIZJh;Ur
$$l1}xUZ&0r<<5e61ne<2SGlq+chEmiKO}g$DJg%XMKnd59iOaY?x?PE1_PvVnR`5@N=S2toU<Wf?_tK3BrAR|&+Gf#%iG>4QU<Hxp%3f~1zorR-
XucKG=I;>Uj*)qpL)Wk8SxTrq{%o$D+H&Hn^fk&o!U|PVP-CA{9JRO95=yNs<4GeC~+EKpl-SD9yeD)SP2Jn*lliM;gS@Ohg2F4)XFSwVIwgF9@Y&i3*gMBX
BkpoDZ(Y<lR6DQ46hvgd`AYb=IPaaa<rNF5v8tn0M-7)4*87W7-uz5j}wdn96uzxn*5`<Vo_-sJ#Ml6ud!CIGv1?C(9-X2PFQxv30q1_-
(CTO3En!40_((4Ihk<`oIw!ARf5}-
iU|$hl5q^oWw;uNOLdeE$bMYn;#WRN)RSbp<ipQ^7WKWCjg~8`(SsvulE&>lX*o4;!eK|4jsJ;ICLafP1Nj@JGaVB1VW|l!^1iOhqRPjE#n30^B|Uo>mo+tc
fs&#W)VGE<bTyVhwzv2ZuivY_I=ykViZ4yyuu!9muool(wTm@Sj@p1~{$tY2lPB%W8~t~P?m7$w{w+vSJd*gQy|(;vd7xcQ?Hiz&GGHd0SS)++eq@zZ{-
H0MeTufh9F^imt0MFK*K#=A!#|Kz%=kA@2W&=R$q1@py#<zI6wS>tf^G^M4F9ghdzE!Ht-Mf|S7tl-OQZYY4;n~GtUQb<TvelCgv#aUlKM5i{RF7>pdD@Z0r
7~g;#x~GDY8D{!`g~@%)k5}7a8Weg3^pJhu+P1+V$_6Eo)qBsl~-
wP>XRXO!|&_oS_La`(E_RoQ=@8xMY$A!7DO2*6|;nImVQfFi2X3KK#O8B{dTADggMUq4=A|N<58p-
x!1SK$9ebs=lpvO;}Nxg>Snr4^UL3d@fNvE*bgUYY+jan3_N|l)hdFBZfzmt;S)@<*_U>BN48^$7ORLvM2(O==G(r8Xr3j7*ZDIa|J+VDd}o$W?5S4lSw)uo
s->bfE~eLv02S|V8wCGh-nBt&+CB#_He#$5rc&{I%qF0EphU|Wy}h3PAtY1Q-
;Ihrgp`H_Tpv<RwSa8cQg{>bA}TzA2KauyXHNW7Zt$i3vo?U`&~$eHkbak5Q4GCpin#!Ud76;Dl6X<FcY3_nVZ}yd#DtOg70SV7BpUxVxPSCKa*$FxKk+a^J
YE;o>&z!4)2sTWWrAPE=-
@N>mxq@XQzXVK#$JMisDU!Zg{w2!r=kaxpv=qlF9+~WU?wagx=l%j4^^cZhzK^t^_`(DG4#%?qNczjv>!q8xNso&i8{^U2zdS$in=h#+Of3TfYTyFT1a0pS^
sK;UUAFZt9j{>-
G9&_7XH|CBK?<vL3|2BOM{vP{4MQn&jNWkR^*%Swb&7!K%)o^`uxPT&1C+!``fqoZDsiBX?};_g6X3rnP#so1BzAN+E}8x~*|b*Di0Wz#nq<gHM|-
R>!F<6dqZ9Pf(ju&v-hE5#P8J@2r8!-
fdlnc5w#N4rc773?ZrM!2+E5ZO^efRzUG~f0f!29}ldTH8Wyxg5|W&O$>A9TV_}zJ4~A^Fh{mis1l@$I=zMI#z$bDaG|^*8tPs2jfmD{NLkV9OI#^H!-
Ej2=mij!2A|xLn}u_mR4-xKRe^dBgjytLho*N;bl%}#NNqC9mLAOCjUGb=MXd*v!YkyP?`Rk$&;AQey>4h!b5U}}2SIaf6W_z-CNaGZ+=*NyZqJCjzbGGkwh
7G)Nn{&@c$=tW&cntm3P2<zuE&p%W8xf=D)lc@6e~_2v^zNF{Y;sCfHb1H7+(*1G#F9PbJNONiOe2TY{ow6g`-
E2)C4$jh~h58x#`Vqm%@6<8|+avfVf2o&{2d>pQTYFJ&g0_@Qq1Jj@Cq(>6T=e)hBI)2(5Fyl^rak2svl}Bg3qZaj_v1i(^B*q%nwEl~)+;jO@r_z9>LA#Qm
)zOW1su6<X%CA1b%uH{6mghY0qyGZLYnJ*7LT)l1YN)AWkp8D4=b5ihG~;n=W<<g(DF?`!G4IsoK)PUot`dO}0v1PX#P#d#GfgLAZe))29#3K{-!%bVs-
RcqfLr)3;?JWvF8Wi`tJ6}nH)bb>DD#V-mW6Iu?og`PVDaLFMjn(3(d;T|`J|JKY%^v3au;Jy@>xK^g-J+~#s-WA-%g9@Bg`zrR-YMX%nBmZn#wbysWAQ6u_
a303F(dC*K1`TGQ*m5qoT3j6bqA{FPE(jHFW`8whgRVV9@)wH1s`Dv<ct@LIbs;w&4az9PZK4%=IjL@S^?l_p%6kSWvs{3?T3%-
b?~RODh8BzThC^RpRR#^2x@h*06^J}3YjkvOg!U&gTCmkiztjq6sH>^!v(Du64Yt3UgYECKm&|E#@7;}w(ri~uS)c^#cwqNq(v>In>g;+L+MzH4s}(n!RH(1
B`6Km1FnGSbL1g<u8buOI1;lmuWGL1{9MTjui+96WIEoLMuuvC5`XOryb^EM`<n~{@*(nV>EyA<S8JrTm9QBJGg+hj+pA1?kf<y462=cdsmlvy-
(aRNaa|VeaGN8C3jd>m1bu=SWlk>HG2li%aLZ#qAt9oeyN~Bs;z+;tnZ25hn4L$|ghG0H@NS^}&Zn%6>71G(csCJ&UkDazIqJTKPW8vvH@EmsWUBL!Wq50Bq
PSn5JLb5G=>SjAg*WEORf0&NPf(TwizAimKK*VvuOCHuycIgrv`Z+FW8^fo-
P|Wj8LtWuCR&yw9PdSHp?7tWgrYW?cE=8m+X+%2hM}M`E|4(e4IQV%!p@HwTk^9*MWqX6*HV@HG{-t=<W&j&J9p|F<f}I(uYU261eN9b-
1GKw^g7sM8eG6AE0Dn{jxr$#@nTJU$HfJ};wOOp^+$9h}Y)WUq)YOLy;IJcsvzn<Pn*+DuuBjGBzl<=V)Fn&j<SmKR*4D8Xj)~ak9K%KqYeka>1eYGKMZKKZ
lKP*i5sgn-QmM<QOTA04kf|K)p#G|;D<NM8<A;He0@7>l-
JSWzvLAtX6qCN;rm}N+E}2VisJ8g)uV^7bcL+a^$BT&MmI|fHjGqO6&9|nnoDk_mEzh`)9Ef@|&s42bRNp2rV74=)gBh|tLp}lk%<06x!vW<oRgYYw;Pr8;3
Z{^eic^y3#;1jsVuO9ha*mc#Ve^M8hwEIL3J7@vIHNOhmn1SB$xgB2nDlV5?LC{@PFj6RZq)9A0~Q!w41(dsuetfmHs^zEi?y3N=DIw#dGb<ZKW+MNCDap6P
r3SID!V9htAY-kLL2%QhLT5r(evlJfLaJl(axh6adRS0_dfiYtF~_<XLD<z6r^wztilw**Tm2RF;wP-
5r8cLX)x@5mTKML6gnWQL@a?SvLjwhx)BJCk%JHPJj~65_BwV>2wdB4{R?`$#fgNfrZ}1$K7rA`AsuU~yH25;vZ2@W$<~p(tFV0-9AHn;m<{+1V>5-
@5BdUCr4Qn{2iO)`b!)(Hirj)ob6Sd!2^%~rr8aj^Wp1470GNCqDV>an&6)&>3p7ah7lklt=W0mkHI)nC)6R7}ga>?|?l*jxoxuEwXv+ObyZKcN>={0FL);N
k>jDG<{v1T(%uBT#gQCS@<liDS6rRCrgn+U{JPkD$q{44>;;*sJ##-pm-
)c8XW}t=Ay!I~e76aac5AS!biJkE%AC)r{@V;P_^WazK+yU8rb9`4x(My<yM7~R~MWzywimzt#OA4t&HdRJg^#2GB;a1=snnxa_PCUW){lBaO^aG#c`FcUt-
Gw@srigKhfiB17;Jl~;^5?x$EFLzaJBSGjbxkdHV-
aT1#R%O@C!$jqwADRylnt@FVV<b<C(Z~mvpu6JK=Ng7zI??jezZnfq*ah)Xb|p-idu0yl)p$S3s8hcOpKnb;fHeN4NYTVX-EyE(`!>V*Y6*|z@M<YTC$}W7i
Q_vqGA68N0N!6JKOlOcISl8@7BzAM54|qZBZEQDFIO9A-wK^S&>JQsL^~L449)*mmlYlw#s|>1Yi9T{x}Qof-
3EWNBZUEV*AFYd{^^z0ZY?~#ti>pC+D||w#bIBq{4j##2$K8ssi@2q-
!Z++XM3iy^zap;wO7P^3wI3{;);Vm^uc7(!5Kv31h63Zy@&KqkB)S^|6Y|U|h0ESG(sA8Agcd=uYTRfkf24BA<%5pkkWD8(+z5`1CJYa!Em!!S<~O!yw2wZ#
mdJE|_?528`_rZA+e%l%T+*P`f&5ku=9eib!*Dk~vt=Yuv9uh~&B0R}iE%3EXnyUuz!OR%*yeFB!X+b!EX2nNfG!;PEl{XNmy@n<3q1Tv(2Y8B#s!x6LE;h%
fj?*m#$3X7k}KMJOt#ic27O2&=+2>)tdDCq27<B-gtb-
c`8^(=mR8b$N}?FWmRr4Xl}7$kRp=MY~p`hC6<v)v%FEhmhlakU!%>wqI$)_UDi~RTzpuF@yvw$DiB|iJHH*SPB#kM;FE=+uIr1!V-
SB<}s=mgKMb(&l`OOqmW}0g`K_UnB8YpdpZj%w7+wX4nW2z7!};OFNn*7uTe9HVF-Ch_h?@#@`p;1fXfP1GI^tHf_B!Roc7!Eo}gho^s7EeB`xLPEGgfhLzO
5e=pcnoFHfGrh@tgk?wN@)k#L&LI((7kXIs@}Iye2h@lC-&qcc~O+*?0>(Rwe}ZB;cJ?o+G(O)-5do*N0Yzvxs=$e5XxsE4Z^w&P-
@e^%V0JP#96SR%I=(m(7Jyr+k_BOO8Yh~W|P4#~RNctUCpI$G{^eXXUHI$C^=f}9##8>d)K4m8JELryrK(`iMD5$XSteESG`^4zYv;EjXSPNxr?L^!Dh9;{j
ey!Fr2Iavn|`FIh3inj~woo1Fz=2rk29UCIQM+*(Nowf=SJ%oYFf&xT9x-Zg+w~fLK`^u!<5MkG(Ow&TzALl^j@h_e-
N1W(Ox^#DfwPuh9V$$0j;)!TK670TpG8(V^0Jze#K3y9`lK;LFGG1(AVBC4^;vY4$Nldi0yS}7aE1oX4B5zHppzJ-
I<8!Kiy5g7A^1qgUibj!JAx?jm<vGt~L4~n#Q)T`L%kg2lu8<+TKCDo@XwP5lk6LUM3%)>ZBdZ`2$GZT>1@?&wG)}9`dr7-
)(3KF38!eFlpe6_FGjgo1eTmm9w~4MhOD!8{kcIl9wJlQ+DMbgHf7aE|W4F~M>^DTYiss@$y6N*<x;14`p#S$?;F-
ckEo#=`;O1{_{AP!t%uUzJ#j4*32^~R_o`pTzF$14o3zjLPe?`@5HfGDvD281T;sKJnau#h~`X1%=tZGPj4iKXM`g&HDxTu<S(A}4w?J0?B%2t)mJUrMqfSU
pg`4BEDlWZKDigOIyA^$=k;D67b_Q9@mcb|#xI;87He^;_o+i>#E(sY&WFrY^;=lVReqeb+a;RlZWfOixIq^0#-
qC!@0M9A_)QN5$ebe`k%5o&p|@|_S_#xe`+{-
Ed>r^JP#*zj<e9imSiOEg5925*;n8WZjhx_06|Qn`$?d~)*owpQGF@h?O8jo?bGYcA+lnLc?{)HigRGL~JJ`7}WwoW1bG1Ik}^o<jkRcDmws+6oXGvcRtCEV
VCmNP3FvNn*AW_BBJ$i$s2Liq_0ADYGyV=*D#=1H}_;esK=VVl<TH<ccSUeOsJZxBH*6p~8gmTlF?!(sB{wFTJ6!9FsHI;`fMT;OiQ23V`FewRcSU+9Vy;vG
iBQDbhJPLAX>^6WlHIGE4-
1{mAci;8j_QduQ&U=Xeu8PJP6U1MPFpwIv|JW$Doe(h$Pr^!*F<T#C<`jHZ1Y7;?L9{78O^61qrUdagv^g5IG?yOqq)w*buP;^i-
5_pf&c*lrsOLXL;I!ViA3_p0FYMNP~b5U^VvlmOHOW{r8Q=`I>yBx@_B8i!IUXo-
*K9c>>#qpwK1Vo1WvUQ;IhZ#PJaeb8M;xNmh(HP^EJ3eF0G#Oh%LxAb@LK47)gVCps?s&+&x>8tNskde8<0vJdHF!>!*^m3SbrRXwV>t(mDCv|(0a5i+l$$r
Mj(<M1b1=Df$F8v21l?d^35*jtErFI9u6|CHirWewb?5y+z-HGOE=`4NQk9d{KBPNRf{Kyugec?TtcVdt&kn7-G-
i1d)fvwCx&X)4*1r$ru;=Adj!}B9xxlJ<fOwnb2v5t9^TUF$0LSy)<K)@7jn3h}uOX=x=zwV9&aSj~^NePy%pQ#C(NxP$ehz7=!S|lK6ERbT3&aSO3`_FE$x
tJ*Y0cy3QeMj7sOl!p5OaAAhu$C6@R(P0=`(6$Y`NDW4b+{YMm_$H|f$ieD_2B*b)!cIAw>B1Z@%*O3MOHCyb7q4Dl4cv};W{c5o1%E~_`j>-
Z1#PIX~p46C}1tid|%=_yzYS)c&Ed^g6I1Ph$j>_>;rS(*OVpnI(hm?LVd$?q_Td2LplDJIfR1_>X(3C@z%a$4yW$HzlqT63`<Y`J^~+eL|rwieq3dw4Y;*`
Q#}pKumzfb!7<%{il!~{Z|L7UR8CXky%^WlsG}w_y29!z$vrKk<_`6(l#Nfl2-
H;8AXvaIKoqqo^J?9PxYMt6(SQc3&^c#fS|~ZuXnBB7d^#s@&hcIm$o<V8&;*K-uaNAM-G4r-
#Phv_jgUy^Z)SlP)vKX&<Pz@4ZNX~QI49Q_>@R3acD@<0qgqb+$!b*m(Njs*V~2U(`^TN=gZkX*o1b{`$AMWXfrz-DGol9Y8^y(`iAWcTzAlog_B$6eb|#|0
bFNBD5XNh9Ve45|1v!}Ay$rjIk(Kq%aF(r_YF2}Uls<ed!1WD5PnQBsj2n;p8DCn51aOx_dXhADT2rxda{BJ`xt|6|5;8aFX0fTo3P{7Tt-
r}746*Q%9r`WUju*415Aol}2mI>4>ojN}(;`a>e=(JewhSPoVJOu<O8sf5Rb8KeNOGo7Z+ElR9x55Bm`f>|?+^85VII{6c!~ZAcR9O`3LT58i|BM-
+*rF)@t}i?^t8%aRXI_m?UO+u-
x0%62~mez4^rk8UF$45n48BxnkVenbr`9fH1C`*1);(Kg3|5VuMNDO%HYkkZ7ZvO*ccu%YYyHv2SIDimfp!`iI^1;X=?lJc2y%KY+||1{)6W{yyacYmGUAFj
wsO;JGKNL{9&mAMeIJ28!{izuRK=JCqX%jXesOTTX>xAYp{pxRgu-
nyFQna#3Bfg@2txww$YdkJdOEWG|%l6F82S}?BBV=1vXY7oU@7HCS4D$ZgcKUa&))%1l=Gkp9Q!^ehFIhq;kRoyxh!sb1~CuCZeI!vOWeg+zIW$Wri-
FI`oMTJuUB%T!9mXxOk&Cy~tV&`&Y9%YV9EnU6D~mWT5Dz#2iH1aWhpHMwbKb^{tOT4T$PAEJ|A=q3){cNqD-BB%vw2`cCNQEXO?_Q~8pOEcqNMd`<$Ta4+L
HE7!3-1KL$9`jd;{;H8ka>3swXdHS9Ut(DVyN-^FYe6iOU+_DEu-z31!(6FzE+0A>6`;t<t2@-
rmT=&SOM{t){bEQR|d3C7rFZt=h=jPHpJ9=mc#2|#gK)ZoY_o3w$Q89K5cXOd>idtQe<s9kyHn2cNJ~cG%j1Bss`$}ZAf5(r|p(&~K{nk)|7#J6~`yhsKAf|
zgbj1_FNl%<Sa%LZ%JsQ+(X=Pzl^3jSvG%qLOo9pNG+Vg1$Sk1O&p+Zd@U6Qx2egXB}_a}uk=_}qZi8YX6LWr#B>0MQ6p@N)%v<Pc2?CJ{8iTjlW7w1phHM9
Ijcal;9yjigdkH;RL@FAnkHT*R1-
vI#lWiw&EUo&F|ePeZ0?zXf~v8#*aA=<7`ARaeT>a^+rw~{*>DnnBBBnHiif``k;CNT!`o%4WyJ$V4#9ZlPuN|kER5#;+%B^wYhxlgORrO~+<Lsu2?)!7=#y
FbQ-p-tX9C7miqt%*&7K95wle`(e~3Z|A;Q78nu(z)&sEYF|FX-
588E9<588J<e$GuqT}(mmjC$t5gOic<&8Jk0dZu=nUa@$|%@(A=u>gP0!PZ8DrbX>8OAcPmt&ezPa`7pFNzeV!bDvtt9J%_u*jcqtw8X9S{;ljNgC%DRJ}t<
GZ$$hU~>29J#2VQW08g#Bf201)Dt?~yKstb^an7{7=aD>`lhy$;M@X{Vy-E?}8(bw~OX=bZud*n$tSTsG26<G@fBlTXxI5_aVYV&Tc-rO;U-
^3GBC5r4Qisf%piwIn`SKhwRV*0Tn?=s=6b#bY1`owH9G(jvWuo9%d@xZy7I8b0QcqW=ABFBy72oJdLay#>7R%)RZ2sgB88L@_DiTh>3J4C6vt`wO-
Z?SH~bkA$hG>SDW|mJ`++=;sSO-I1CLSwHiZWowh~?o14OD2yj-lJg<h=@owhHx@tKy&xgDtT01wwK--tA{x_eH&8c`M{aTQ)wIGy=`vzl&N8T4@%7}fkHF^
8=hxO!o^q(g85l#~ud7e5ouM~!5kg0QXj-
7JR&sM7MZZ{ZVHq;ik|x)uc9YnkvC7S1`!tL=ahKxH9=wH9kUeAr9?=pl>30eaBUOPUnZf8=<>Kn@u*#gi^5*L?@<iS^EM-
{KM0g%i&(a4!@IR)l%{fWLo+OP+%%}qN<L%qljw4(0QC|wQu9t2?+PAvSLd-Z=#iqL#V<Ny3{LME)-
Jbs`xiT+Kc1(bE%Dipp!e`~mKkhFYll{rpLXq9D&nskk0nJcez5&BmcM47n01W^DbFx0?ryAao00Gd90kr!A1kKm6vBYQl0ssI200dcD
"""
_MOBILE_SHA256 = '1556296978943e1faf0222f66fe39b8cf178ac06b62e433557075976ba53bdbb'
try:
    _mobile_text = ''.join(_MOBILE_PAYLOAD.split())
    if len(_mobile_text) != 22545:
        raise ValueError('文字数不一致')
    _mobile_bytes = _mobile_lzma.decompress(_mobile_b64.b85decode(_mobile_text))
    if _mobile_hash.sha256(_mobile_bytes).hexdigest() != _MOBILE_SHA256:
        raise ValueError('内容不一致')
    _mobile_source = _mobile_bytes.decode('utf-8')
    _mobile_filename = '<'+_MOBILE_BUILD+'>'
    _mobile_code = compile(_mobile_source,_mobile_filename,'exec')
except Exception as _mobile_error:
    raise SystemExit('貼り付け内容が不完全か変化しています。ファイル全体を貼り直してください。'
                     +' ('+type(_mobile_error).__name__+')') from None
if __name__ == '__main__':
    if '--show-source' in _mobile_sys.argv:
        print(_mobile_source,end='')
        raise SystemExit(0)
    print('【起動版】'+_MOBILE_BUILD+' / 内容確認OK',flush=True)
    if '--check-only' in _mobile_sys.argv:
        raise SystemExit(0)
_mobile_cache.cache[_mobile_filename] = (len(_mobile_bytes),None,
                                        _mobile_source.splitlines(True),_mobile_filename)
exec(_mobile_code,globals())
if __name__ == '__main__':
    raise SystemExit(0)
# END v20-fetch-retry-20261105-mobile1
