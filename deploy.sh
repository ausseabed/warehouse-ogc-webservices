## Helper function for doing a deploy

CURRENT_TAG=`git tag -l | grep deploy | sort -t "/" -k 3 | tail -1`

echo
echo The current tag is $CURRENT_TAG
echo
echo "Update ci agent with TF_VAR_geoserver_snapshot_iso_datetime = "
date +%Y-%m-%dT%H:%M:%S%z
echo
echo "At time of writing this was found at:"
echo "https://app.circleci.com/settings/project/github/ausseabed/warehouse-ogc-webservices/environment-variables?return-to=https%3A%2F%2Fapp.circleci.com%2Fpipelines%2Fgithub%2Fausseabed%2Fwarehouse-ogc-webservices"
echo

LAST_DIGIT=`echo $CURRENT_TAG | sed "s/.*\.//"`

NEXT_DIGIT=`echo "$LAST_DIGIT + 1" | bc`

NEXT_TAG=`echo $CURRENT_TAG | sed "s/\.[^.]*$/.$NEXT_DIGIT/"`

echo "Push a new tag to the repository (e.g. $NEXT_TAG)"
echo
echo git checkout master
echo git pull
echo git tag $NEXT_TAG
echo git push origin $NEXT_TAG
echo
echo Visit ci and approve the push to production
echo "https://app.circleci.com/pipelines/github/ausseabed/warehouse-ogc-webservices"
echo