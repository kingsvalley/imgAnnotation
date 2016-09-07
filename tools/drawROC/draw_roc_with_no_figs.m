%ͼƬ������path���棬����Ϊ�ϲ�·��+png
function draw_roc_with_no_figs(path)
labe_num=find(path=='/');
name_fig=path((labe_num(end-1))+1:(labe_num(end)-1));
files= dir(fullfile(path,'*.txt'));
lengthfiles = length(files);
% end
name_fig=[name_fig,'.png'];
for i=1:lengthfiles
data_label=load([path files(i).name]);
label{i}=data_label(:,1);
data{i}=data_label(:,2);
name{i}=files(i).name;
%[tp, fp] = roc(label, data);
end
plott.color={{'color','r'},{'color','g'},{'color','b'},{'color','h'},{'color','y'},{'color','k'}};
plott.line={{'.'},{'--'},{'-'},{'-.'},{'--'},{'-.'}};
plott.linewidth={{'linewidth', 2}};
plott.name=name;
set(0,'DefaultFigureVisible', 'off')
draw_prc(label,data,1,plott)
print(gcf,'-dpng',[path name_fig]) 
close all;
end
