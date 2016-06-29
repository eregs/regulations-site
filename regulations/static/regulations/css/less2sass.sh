
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

echo "converting mixins..."
sed -i.bak -e 's/^\./@mixin /g' mixins.scss
sed -i.bak -e 's/\.cf-icon__rotate/@include cf-icon__rotate/g' cf-icons.scss
sed -i.bak -e 's/\.cf-icon__flip/@include cf-icon__flip/g' cf-icons.scss
sed -i.bak -e 's/\..cf-icon-ie7/@include cf-icon-ie7/g' cf-icons.scss

echo "renaming variables..."
find . -type f -exec sed -i.bak 's/\$80_gray/\$gray_80/g' {} \;

# remove backup files from stream editing
rm *.bak **/*.bak

# go back to css folder
cd ../



