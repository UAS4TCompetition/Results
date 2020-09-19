function [tr]=Rnan(tr)
% remove all NaN at the end of the row
while isnan(tr(end))
    tr(end)=[];
end