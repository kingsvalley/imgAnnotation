function draw_roc(path)
files= dir(fullfile(path,'*.txt'));
lengthfiles = length(files);
% end
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
draw_prc(label,data,1,plott)
end
