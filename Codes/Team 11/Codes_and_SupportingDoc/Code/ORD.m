function [t_lat,t_lon,t_speed,t_lon_acc,t_lat_acc,t_time]=ORD(temp);
% this function orders the points of the trajectory
% it uses the fact that 
%1-lat and lon are the first and second elments in each point in the trajectory
%2- all the trajectories points share the first two digits of the lat and the first two digits of the long
% So it is easy to identify the points of the trajectory and order them
temp=temp(2:end);% remove the first element
ind=find(floor(temp)==23);
indd=find(floor(temp(ind-1))==37);
st=ind(indd)-1;
t_lat=nan(length(st),1);
t_lon=nan(length(st),1);
t_speed=nan(length(st),1);
t_lon_acc=nan(length(st),1);
t_lat_acc=nan(length(st),1);
t_time=nan(length(st),1);

for i=1:length(st)-1
    if (st(i+1)-st(i))==6
        t_lat(i)=temp(1,st(i));
        t_lon(i)=temp(1,st(i)+1);
        t_speed(i)=temp(st(i)+2);
        t_lon_acc(i)=temp(1,st(i)+3);
        t_lat_acc(i)=temp(1,st(i)+4);
        t_time(i)=temp(1,st(i)+5);
    end
end
t_lat(i)=temp(1,st(end));
if (st(end)+1)<=length(temp)
    t_lon(i)=temp(1,st(end)+1);
end
if (st(end)+2)<=length(temp)
    t_speed(i)=temp(st(end)+2);
end
if (st(end)+3)<=length(temp)
    t_lon_acc(i)=temp(1,st(end)+3);
end
if (st(end)+4)<=length(temp)
    t_lat_acc(i)=temp(1,st(end)+4);
end
if (st(end)+5)<=length(temp)
    t_time(i)=temp(1,st(end)+5);
end




