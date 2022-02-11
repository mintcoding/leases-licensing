#!/bin/bash
## first parameter is DBCA branch name, optional second parameter is an integer indicating incremental daily version
set -e
if [[ $# -lt 1 ]]; then
    echo "ERROR: DBCA branch must be specified"
    echo "$0 1"
    exit 1
fi
if [[ $# -gt 1 ]] && ! [[ $2 =~ ^[0-9]+$ ]]; then
    #echo "ERROR: Must specify integer indicating incremental daily version e.g."
    echo "ERROR: Incremental daily version must be an integer"
    echo "$0 1"
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
#REPO=$(basename -s .git `git config --get remote.origin.url` | sed 's/-//g')
REPO=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/-//g'|sed 's/....$//'))
DBCA_BRANCH="dbca_"$1
BUILD_TAG_NO_INCREMENT=dbcawa/$REPO:$1_v$(date +%Y.%m.%d)
if [[ $# -gt 1 ]]; then
    INCREMENT=$2
else
    INCREMENT=1
    if [[ $(docker images | awk '{print $1":"$2}' | grep $BUILD_TAG_NO_INCREMENT) ]]; then
        DAILY_IMAGE_INCREMENTS=$(docker images | awk '{print $1":"$2}' | grep $BUILD_TAG_NO_INCREMENT)
        declare -i I=0
        declare -A inc_array
        for DAILY in $DAILY_IMAGE_INCREMENTS;
        do
            #INC=$(echo $DAILY | cut -c $((${#REPO}+21))-)
            INC=$(echo $DAILY | cut -c $((${#REPO}+${#1}+22))-)
            inc_array[$I]=$INC
            I=$(($I+1))
        done
        declare -i max_value=0
        for ii in ${inc_array[@]};
        do
            if [ $ii -gt $max_value ]; then
                max_value=$ii
            fi;
        done
        INCREMENT=$((max_value+1))
    fi
fi
#BUILD_TAG=dbcawa/$REPO:v$(date +%Y.%m.%d).$INCREMENT
BUILD_TAG=$BUILD_TAG_NO_INCREMENT.$INCREMENT
{
    git checkout $DBCA_BRANCH
} ||
{
    echo "ERROR: You must have your local code checked in and the DBCA branch set up on local with the 'dbca_' prefix.  Example Instructions:"
    echo "git remote add dbca git@github.com:dbca-wa/wildlifecompliance.git"
    echo "git checkout -b dbca_compliance_mgt_dev dbca/compliance_mgt_dev"
    echo "$0 1"
    exit 1
}
{
    git pull &&
    cd $REPO/frontend/$REPO/ &&
    npm run build &&
    cd ../../../ &&
    source venv/bin/activate &&
    #./manage.py collectstatic --no-input &&
    $(find . -maxdepth 1 -name "manage*.py") collectstatic --no-input &&
    git log --pretty=medium -30 > ./git_history_recent &&
    docker image build --no-cache --tag $BUILD_TAG . &&
    git checkout $CURRENT_BRANCH
    echo $BUILD_TAG
} ||
{
    git checkout $CURRENT_BRANCH
    echo "ERROR: Docker build failed"
    echo "NB: This script assumes that your virtual environment folder is 'venv'"
    echo "$0 1"
    exit 1
}
{
    docker push $BUILD_TAG
} || {
    git checkout $CURRENT_BRANCH
    echo "ERROR: Docker push failed"
    echo "$0 1"
    exit 1
}
