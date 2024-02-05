
function AdDW=AdDW(qpo,element2,N,sF,FO)
% given a set of obs and an adcirc mesh (element connectivity and x,y
% returns a structure identifying nodes of the element that the point falls
% within.  Also returns coordinates and other info.
% First finds the index of the nearest node - then finds elment and inverse
% distance weights for averaging

% qpo - x,y of query point of interest (obs)
% element2 - telement connectivity matrix
% N =[x y]
sz=size(qpo);
lqp=sz(1);
%%
   x=N(:,1); y=N(:,2);
    for j=1:size(qpo,1)
        for i=1:length(N)  
        dist(i)=lldistkm([qpo(j,1) qpo(j,2)],N(i,:));
        disti(i)=i;
        end
        mindist=min(dist);
        dist2=dist';
        [C, Ci]=sortrows(dist2,'ascend');
        ind1=find(dist==min(dist));
        qpe(j)=Ci(1);   %index of closest node
        qpe2(j)=Ci(2);   %index of closest node
    end
    %% for TEST
%      x2=N(:,1); y2=N(:,2);
%      N2 =[x2 y2];
%      qpo=[-71.7053870000000,41.3326400000000]
%         for i=1:length(N) 
%             disti(i)=i;
%         dist2(i)=lldistkm([qpo(1,1) qpo(1,2)],N2(i,:));        
%         [d1km d2km]=lldistkm([qpo(1,1) qpo(1,2)],N2(Ci(2),:));        
%         end      
%         dist3=dist2';
%         [C, Ci]=sortrows(dist3,1,'ascend');
%         mindist=min(dist2);
%          indi=find(dist2==min(dist2));
%           hhh=Ci(1);
%           hh=scatter3(x(hhh),y(hhh),y(hhh)*999,55,'filled');hh.MarkerFaceColor='m'
%%
    for i=1:size(qpo,1)
        ID=qpe(i);  e.nn(i)=ID;
        ind1=find(element2(:,1)==ID);
        ind2=find(element2(:,2)==ID);
        ind3=find(element2(:,3)==ID);
        inda=cat(1,ind1,ind2,ind3);  % the three nodes that bound the point
        T=element2(inda,:);
        
        %second try
        ID2=qpe2(i);  e2.nn(i)=ID2;
        ind12=find(element2(:,1)==ID2);
        ind22=find(element2(:,2)==ID2);
        ind32=find(element2(:,3)==ID2);
        inda2=cat(1,ind12,ind22,ind32);  % the three nodes that bound the point
        T2=element2(inda2,:);
        
                       figure(FO); hold on
                      
            for j=1:size(T,1)
                xT=x(T(j,:));
                yT=y(T(j,:));
                pgon = polyshape(xT,yT);
                 subplot(1,2,1);hold on
                plot(pgon);
                plot(qpo(1),qpo(2),'om');
%                 gg=plot(x(ID),y(ID),'sr');
%                 gg.MarkerSize=55;
   
                TFin = isinterior(pgon,qpo(i,1),qpo(i,2));
                 if(sum(TFin)>0)       % if original worked               
                        e.ID(i,1)=inda(j);
                        e.N(i,:)=T(j,:);
                        e.x(i,1:3)=xT';
                        e.y(i,1:3)=yT';
                            for k=1:3
                            e.dist(i,k)=lldistkm([qpo(i,1) qpo(i,2)],N(e.N(k),:)); 
                            e.inv(i,k)=1/e.dist(i,k);
                            end
                            junk=sum(e.inv(i,:));
                            e.wt(i,:)=e.inv(i,:)/junk;
                            
                            indm=find(e.dist==0);   % find a query point that is co-located with a mesh node
                            if(~isempty(indm))
                                e.wt(indm)=1;
                            end                            
                 end
            end
    
               if isfield(e,'wt') == 0
                subplot(1,2,2);hold on
%                 if(sum(TFin)==0) % try second closest node  
                for j=1:size(T2,1)
                xT=x(T2(j,:));
                yT=y(T2(j,:));
                pgon = polyshape(xT,yT);
                plot(pgon);
                plot(qpo(1),qpo(2),'r^');
%                 gg=plot(x(ID2),y(ID2),'sr');
%                 gg.MarkerSize=55;
                
                e.ID(i,1)=inda2(j);
                e.N(i,:)=T2(j,:);
                e.x(i,1:3)=xT';
                e.y(i,1:3)=yT';
                  for k=1:3
                   e.dist(i,k)=lldistkm([qpo(i,1) qpo(i,2)],N(e.N(k),:)); 
                   e.inv(i,k)=1/e.dist(i,k);
                   end
                   junk=sum(e.inv(i,:));
                   e.wt(i,:)=e.inv(i,:)/junk;                                               
         
                end
               end
            
            
                   if(sF<1)
                   close(figure(FO))
                   else
                   end
    end
    %%
AdDW=e;
end