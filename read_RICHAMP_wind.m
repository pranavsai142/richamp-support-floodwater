clear; clc;close all; pd=pwd;nfig=0;
FS=12;FA=0.5;
satn='subset'
% load coastlines; coastz(1:length(coastlat))=100;
%%
inp=getenv("RICHAMP_INDIR")+"/"; idir=inp{1};
E=importdata('RTF_RI.txt');EE=E.data
%% make scen name and output dir
k = strfind(idir,'/');scen=idir((k(end-2)+1):(k(end-1)-1));   odir=[scen '_OUT/Wind' '/']; status = mkdir(odir); 
if(status==0)
    mkdir(odir)
end
%%
wnc=('RICHAMP_wind.nc');
tref=datenum(1990,1,1);

infile=[idir wnc]
lfn=length(infile);
ftime=infile(lfn-12:lfn-3)
time0=ncread([infile],'/Main/time');
time1=tref+time0/1440;
time2=tref+time0/1440;
tstr=datestr(time1);
tstr2=datestr(time2);

lon=ncread(infile,'/Main/lon');
alat=ncread(infile,'/Main/lat');
aspd=ncread(infile,'/Main/spd');
adir=ncread(infile,'/Main/dir');

% % if need to flip lat, u, v, pres
blat=flipud(alat);
[lon_m,lat_m]=meshgrid(lon,alat);
spd2=permute(aspd,[2,1,3]);
maxS=max(spd2,[],3);
%%
[lon_m1,lat_m1]=meshgrid(lon,alat);
bspd2=permute(aspd,[2,1,3]);
bspd3=flipud(bspd2);
bmaxS=max(bspd3,[],3);
%%
nfig=nfig+1; figure(nfig);set(gcf,'color','w');
[ortho, cmap] = imread(cat(2,satn,'.png'));R = worldfileread(cat(2,satn,'.pgw'), 'planar', size(ortho)); mapshow(ortho,cmap,R);hold on
    pp=pcolor(lon_m,lat_m,maxS); set(gca,'FontSize',FS, 'FontWeight','b');view(0,90); shading interp
    set(pp,'facealpha',FA)    
    colormap(jet);h=colorbar;caxis([0 30]);h.Label.String=({'Wind Speed (m/s)'});  h.Label.FontSize=FS; 
    
    for i=1:4
hh=scatter3(E.data(i,2),E.data(i,1),(E.data(i,1)*0+999),40,'filled','MarkerFaceColor','w');
    end
ylim([R.YWorldLimits(1)+.1 R.YWorldLimits(2)-0.00]);	set(gca,'FontSize',FS, 'FontWeight','b')
xlim([R.XWorldLimits(1) R.XWorldLimits(2)]);xtickformat('%.0f'); ylabel('Latitude (^oN)'); xlabel('Longitude (^oE)')
hh=suptitle({'GFS Forecast - Max Wind Speed';[tstr(1,:) ' through ' tstr(end,:)]}); hh.FontSize=20; hh.FontWeight='b';
set(gcf,'color','w');   ffn=cat(2,odir,'GFS_MaxSPD', '_', satn,'.png');saveas(gcf,ffn);   ax = gcf;   exportgraphics(ax,ffn,'Resolution',300) 
%%
X=lon_m;     Y=lat_m;

ii=0;
    for i=1:4
    Xq=E.data(i,2);     Yq=E.data(i,1);
        for j=1:121
         Vq = interp2(X,Y,spd2(:,:,j),Xq,Yq);
         sp(j,i)=Vq;
        end
    end   
   %% 
nfig=nfig+1; figure(nfig);
plot(time1,sp,'LineWidth',2); set(gca,'FontSize',20, 'FontWeight','b')
ylabel('Wind Speed (m/s)'); set(gca,'FontSize',14, 'FontWeight','b')
legend('Newport','Quonset','Providence','Offshore-NITR','FontSize',20,'FontWeight','b')
xlim([time1(1) time1(end)])
set(gca,'XTick',(time1(1):(6/24):time1(end)))
datetick('x','mm/dd-HH','keepticks');
grid on
set(gcf,'color','w');   ffn=cat(2,odir,'TS_Wind','.png');ax=gcf;exportgraphics(ax,ffn,'Resolution',300)
