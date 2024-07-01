function [out]=trackll_2num(IN)    

A=IN;
sz=size(A);

c1=(A(:,1));
c2=(A(:,2));

for i=1:sz(1)
    latstr=c1(i);
    latstrlength=strlength(latstr);
    latstr=char(latstr);
    lat=latstr(1,1:end-1);
    Ao(i, 1)=(str2double(lat))/10;
    if(contains(latstr,'S'))
        Ao(i,1)=-Ao(i,1);
    end

    lonstr=c2(i);
    lonstr=char(lonstr);
    lon=lonstr(1,1:end-1);   
    Ao(i,2)=(str2double(lon))/10;

    if(contains(lonstr,'W'))
        Ao(i,2)=-Ao(i,2);
    end
        
end

out=Ao;
disp(out);
end