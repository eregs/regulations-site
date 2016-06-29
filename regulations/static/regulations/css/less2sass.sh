
#########
# less2sass BASH script
#
# Description:
# Copy conversion of the files in /less (*.less) to /scss (.scss)
#
# Originally written by xtine
#########

# check if npm package is installed
# from https://gist.github.com/JamieMason/4761049
function npm_package_is_installed {
  # set to 1 initially
  local return_=1
  # set to 0 if not found
  ls /usr/local/lib/node_modules | grep $1 >/dev/null 2>&1 || { local return_=0; }
  # return value
  echo "$return_"
}

if [ ! $(npm_package_is_installed less2sass) ]
  then
    echo "npm package less2sass not found, installing now..."
    npm install -g less2sass
fi

echo "npm package less2sass found, running conversion..."

# make sass directories
mkdir -p scss scss/module

# convert less to scss files
less2sass less scss

# copy the scss files to appropriate directories
cd less
mv *.scss ../scss
cd module
mv *.scss ../../scss/module

# back to created scss folder
cd ../../scss

# fixing less to sass conversion errors
echo "converting mixins..."
sed -i.bak -e 's/^\./@mixin /g' mixins.scss
sed -i.bak -e 's/\.cf-icon__rotate/@include cf-icon__rotate/g' cf-icons.scss
sed -i.bak -e 's/\.cf-icon__flip/@include cf-icon__flip/g' cf-icons.scss

echo "correcting mixin font extends..."
sed -i.bak -e 's/&:extend(\.font-bold)/@include font-bold/g' mixins.scss
sed -i.bak -e 's/&:extend(\.font-regular)/@include font-regular/g' mixins.scss

echo "correcting cf-icon, font-awesome, group extends in stylesheets..."
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' mixins.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' typography.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' module/interpretations.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' module/header.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' module/sidebar.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' module/expandables.scss
sed -i.bak -e 's/@include cf-icon/@extend .cf-icon/g' module/sidebar.scss
sed -i.bak -e 's/@include cf-icon__spin/@extend .cf-icon__spin/g' mixins.scss
sed -i.bak -e 's/\.fa/@extend .fa/g' module/comment-review.scss
sed -i.bak -e 's/@include group/@extend .group/g' module/sidebar.scss
sed -i.bak -e 's/\$page/@page/g' print.scss

echo "correcting @keyframe, image @2x, @print declarations..."
sed -i.bak -e 's/\$-webkit-keyframes/@-webkit-keyframes/g' cf-icons.scss
sed -i.bak -e 's/\$-webkit-keyframes/@-webkit-keyframes/g' font-awesome.scss
sed -i.bak -e 's/\$2x/@2x/g' module/interpretations.scss
sed -i.bak -e 's/\$2x/@2x/g' module/sidebar.scss

echo "renaming incompatible variables..."
find . -type f -exec sed -i.bak 's/\$80_gray/\$gray_80/g' {} \;

# remove backup files from stream editing
rm *.bak **/*.bak

# go back to css folder
cd ../

