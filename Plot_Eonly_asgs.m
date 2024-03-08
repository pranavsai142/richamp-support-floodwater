clear; clc; nfig=0; close all;
 inp=getenv("RICHAMP_INDIR")+"/"; idir0=inp{1};
E=importdata('RTF_RI.txt');EE=E.data
%% make scen name and output dir
k = strfind(idir0,'/');scen=idir0((k(end-2)+1):(k(end-1)-1));   odir=['graphs' '/']; status = mkdir(odir); 
if(status==0)
    mkdir(odir)
end
%%
nc=[idir0 'fort.63.nc'];
%% read tref vs assign tref=datenum(2007,4,1,6,0,0);
av = ncreadatt(nc,'time','base_date')
yr=av(1:4);  mo=av(6:7);  da=av(9:10);  hr=av(12:13); %hr='6';
tref=datenum(str2num(yr),str2num(mo),str2num(da),str2num(hr),0,0);
trefs=datestr(tref)
% tref=datenum(2022,12,15)
%% read in output
wse0= ncread(nc,'zeta'); x= ncread(nc,'x'); y= ncread(nc,'y'); z= ncread(nc,'depth'); t0= ncread(nc,'time'); t=tref+(t0/86400)-0;
element=ncread(nc,'element');element2=element';element2=double(element2);clear element
%% TS for water level stations
N=[x y];
sF=0;
%%  Get the maximum elevation from the run, and make the inundation 
TH=0;  
TH=1;
max_elev=nanmax(wse0,[],2);         
inun=max_elev+z;                  
ind=find(z>TH);                     % finding nodes that are at elevations greater than TH
inun(ind)=NaN;                       % assigning nan to nodes < MSL to blank them out
%%
sats={'subset';};satn=sats{1};
%%
G.x=x;G.y=y;G.nm=element2;G.dp=z;grd=G;
nfig=nfig+1; figure(nfig)
[ortho, cmap] = imread(cat(2,satn,'.png'));R = worldfileread(cat(2,satn,'.pgw'), 'planar', size(ortho)); mapshow(ortho,cmap,R);hold on
yrng=([R.YWorldLimits(1)-.06 R.YWorldLimits(2)+0.06]);xrng=([R.XWorldLimits(1)-.05 R.XWorldLimits(2)+.05]);
fignum=nfig;[xs,ys,depths,elements,nn_news,ii]=subset_plot_mesh2(grd,xrng,yrng,fignum);zs=z(ii);
close all
%% E
FA=0.5;
nfig=nfig+1; figure(nfig);
[ortho, cmap] = imread(cat(2,satn,'.png'));R = worldfileread(cat(2,satn,'.pgw'), 'planar', size(ortho)); mapshow(ortho,cmap,R);hold on
trisurf(elements,xs,ys,(max_elev(ii)),'FaceAlpha',.5,'EdgeColor',[0.85 0.85 0.85]); view(0,90); 
hold on
for i=1:4
hh=scatter3(E.data(i,2),E.data(i,1),(E.data(i,1)*0+999),40,'filled','MarkerFaceColor','w');
end
shading interp  
colormap(jet);h=colorbar;caxis([0 3]);
h.Label.String=({'Elevation (m NAVD88)';});h.FontSize=16; h.FontWeight='b';h.Ruler.TickLabelFormat = '%3.2f';
ylim([R.YWorldLimits(1)+.002 R.YWorldLimits(2)-0.00]);	set(gca,'FontSize',16, 'FontWeight','b')
xlim([R.XWorldLimits(1) R.XWorldLimits(2)]);
set(gca,'XTick',[]);set(gca,'YTick',[])
set(gcf,'color','w');   ffn=cat(2,odir,satn,'maxE','.png'); ax = gcf; exportgraphics(ax,ffn,'Resolution',300) 
%%
sF=0
for i=1:length(EE)
    FO=9999+i;
qpo=[EE(i,2) EE(i,1)];
AA=AdDW(qpo,element2,N,sF,FO);
mm=(AA.wt)';
mm1=(wse0(AA.N,:)).*mm;  mm2=sum(mm1); W1(:,i)=mm2;  %wse
mm1=(z(AA.N,:)).*mm;  mm2=sum(mm1); W5(:,i)=mm2;  %z
end
%%
LW=2
psub=[1:4];
FS=12;t2=t;
i1=1; i2=length(EE);
t2s=datestr(t2);
nfig=nfig+1;figure(nfig)
plot(t2,W1(:,psub),'LineWidth',LW);set(gca,'FontSize',FS, 'FontWeight','b');hold on
datetick('x','mm/dd-HH','keepticks');   grid on; grid minor;
ylabel('Zeta (m)')
legend('Newport','Quonset','Providence','Offshore-NITR')
set(gcf,'color','w');   ffn=cat(2,odir,'TS1','.png');ax=gcf;exportgraphics(ax,ffn,'Resolution',300)
