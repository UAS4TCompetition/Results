[TR]=pre_processingv3();% prepare the data
ply=kml2struct('Leof. Alexandras.kml');% reading the kml file to get the three polygons
%filtering the trajectories based on ploygons and heading
for k=1:length(TR)
                    TR{k,8}=-1;% intialize the value to -1

    for p=1:3
        [in,on] = inpolygon(TR{k,7}.lat,TR{k,7}.lon,ply(p).Lat,ply(p).Lon);
        if sum(in)>2
            A=find(in==1);
            [arclen1,az] = distance(ply(3+2*(p-1)+1).Lat,ply(3+2*(p-1)+1).Lon,TR{k,7}.lat(A(1)),TR{k,7}.lon(A(1)));
            [arclen2,az] = distance(ply(3+2*(p-1)+2).Lat,ply(3+2*(p-1)+2).Lon,TR{k,7}.lat(A(1)),TR{k,7}.lon(A(1)));
            [arclen3,az] = distance(ply(3+2*(p-1)+1).Lat,ply(3+2*(p-1)+1).Lon,TR{k,7}.lat(A(end)),TR{k,7}.lon(A(end)));
            [arclen4,az] = distance(ply(3+2*(p-1)+2).Lat,ply(3+2*(p-1)+2).Lon,TR{k,7}.lat(A(end)),TR{k,7}.lon(A(end)));
            if arclen3>arclen1 &arclen4<arclen2
                TR{k,8}=p;
            end
        end
    end
end
TR=TR(find(cell2mat(TR(:,8))==2),:);
RP=kml2struct('Reference Point.kml');
ply=kml2struct('Orange polygon lanes.kml');% reading the kml file to get the three polygons
plye=kml2struct('Orange polygon lanes - Extended.kml');% reading the kml file to get the three polygons

% transforming to plan---------
    flatearth_points=[];
   for p=3:4
       flatearth_points = [flatearth_points;lla2flat([ply(p).Lat,ply(p).Lon,0],[RP.Lat(1),RP.Lon(1)],0,0)]; 
   end
%---------------
for k=1:size(TR,1)
    TR{k,7}.lane=-1*ones(height(TR{k,7}),1);
    rm=find( isnan(TR{k,7}.lat) | isnan(TR{k,7}.lon));
       TR{k,7}(rm,:)=[];
       flatearth_pos = lla2flat([TR{k,7}.lat,TR{k,7}.lon,zeros(length(TR{k,7}.lat),1)],[RP.Lat(1),RP.Lon(1)],0,0);
   TR{k,7}.x=flatearth_pos(:,1);
   TR{k,7}.y=flatearth_pos(:,2);
    
    
    
   for p=1:2
       [in,on] = inpolygon(TR{k,7}.lat,TR{k,7}.lon,ply(p).Lat,ply(p).Lon);
       TR{k,7}.lane(in)=p;
      TR{k,7}.distance(in)=pdist2([TR{k,7}.x(in) TR{k,7}.y(in)],flatearth_points(p,1:2));
       
   end
   st=find(TR{k,7}.distance~=0,1);
   if~isempty(TR{k,7}.distance(1:st-1))
       for p=1:2
           [in,on] = inpolygon(TR{k,7}.lat(1:st-1),TR{k,7}.lon(1:st-1),plye(p).Lat,plye(p).Lon);
           in(st:length(TR{k,7}.lat))=0;
           TR{k,7}.lane(in)=p;
           TR{k,7}.distance(in)=-pdist2([TR{k,7}.x(in) TR{k,7}.y(in)],flatearth_points(p,1:2));
       end
   end
   
   %% imputing zeros
      st=find(TR{k,7}.distance~=0,1);
en=find(TR{k,7}.distance~=0,1,'last');
idx=find(TR{k,7}.distance(st:en)~=0);
idxx=find(TR{k,7}.distance(st:en)==0);
TR{k,7}(find(diff(TR{k,7}.time)>1,1),:)=[];
if ~isempty(idxx)
    if length(unique(TR{k,7}.distance(st+idx-1)))~=length(TR{k,7}.distance(st+idx-1))
%           [m,n]=sort(TR{k,7}.distance(st+idx-1),'ascend');
%         x=TR{k,7}.time(st+idx-1);
        
        yi = interpn(TR{k,7}.time(st+idx-1),TR{k,7}.distance(st+idx-1),TR{k,7}.time(st+idxx-1),'linear');
              % yi = interpn(x(n),m,TR{k,7}.time(st+idxx-1),'cubic');

    else
        no=.00001*randn(length(TR{k,7}.distance(st+idx-1)),1);
        [m,n]=sort(no,'ascend');
        %x=TR{k,7}.time(st+idx-1);
                yi = interpn(TR{k,7}.time(st+idx-1)+m,TR{k,7}.distance(st+idx-1),TR{k,7}.time(st+idxx-1),'linear');

          % yi = interpn(x(n),TR{k,7}.distance(st+idx-1)+m,TR{k,7}.time(st+idxx-1),'cubic');

    end
   TR{k,7}.distance(st+idxx-1)=yi;
end
   writetable(TR{k,7},strcat('C:\Users\elhenawy\OneDrive - Queensland University of Technology\compition\orange_poly\T',num2str(k),'.csv'));
end

