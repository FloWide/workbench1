#!/bin/bash


usage() { 
    echo "Usage: ${0} -o <OWNER> -r <REPO> -f <FILE> -v [VERSION]"
    exit 1
}



while getopts ":o:r:f:v:" o; do
    case "${o}" in
        o)
            OWNER=${OPTARG}
            
            ;;
        r)
            REPO=${OPTARG}
            ;;
        f)
            FILE=${OPTARG}
            ;;
        v)
            VERSION=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "${OWNER}" ] || [ -z "${REPO}" ] || [ -z "${FILE}" ]; then
    usage
fi

if [ -z "${VERSION}" ]; then
    VERSION="latest"
fi



API_URL="https://api.github.com/repos/$OWNER/$REPO"

if [ $VERSION = "latest" ]; then
    ASSET_ID=$(curl $API_URL/releases/latest | jq -r '.assets[] | select(.name == "'$FILE'").id' )
else
    ASSET_ID=$(curl $API_URL/releases/tags/${VERSION} | jq -r '.assets[] | select(.name == "'$FILE'").id' )
fi

if [ -z $"$ASSET_ID" ] || [ $ASSET_ID = "null" ]; then
    echo "Couldn't find asset id"
    exit 1
fi
echo $ASSET_ID

if [ -f "$FILE" ]; then
    rm -f $FILE
fi

curl -O -J -L -H "Accept: application/octet-stream" "$API_URL/releases/assets/$ASSET_ID"