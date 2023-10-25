#age: bash getTopN.sh --n 1 --stage 1 task.trials task.score

n="1 5 10 20"
stage=1
speed=true

. utils/parse_options.sh

trials=$1
score=$2

for x in $trials $score;do
[ ! -f "$x" ] && echo "Expected $x to exist." && exit
done

if [ "$stage" -le 1 ];then
echo "[stage 1] Generate labeled score and sort it."
awk -v speed=$speed 'NR==FNR{a[$1$2]=$3}NR>FNR{
if(speed=="true"){
    if($3>-10){
        print $0,a[$1$2]
    }
}else{
print $0,a[$1$2]
}}' $trials $score | sort -k2,2 -k3gr,3  > $score.label.sorted
fi

for i in $n;do
if [ "$stage" -le 2 ];then
echo "[stage 2] Count hit times with top-$i."
awk -v n=$i 'BEGIN{spker="";count=0;total=0;}{
if($2!=spker){
spker=$2;
count=0;
}
if(count<n){
    if($4=="target"){
        total=total+1;
        count=n;
    }
    count=count+1;
}}END{
print total;
}' $score.label.sorted
fi
done


