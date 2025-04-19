# aes-tool - A simple encryption tool
# Copyright (C) 2025 Md. Zaif Imam Mahi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.



# extract your zip file then move thatdirectory to the $HOME directory.
# first enter that directory if you do it manually
# run that line mark by "#run it  ..." and your done


# install dependencies
sudo apt update && sudo apt install python-tk # run it ...1 

if [ $? -eq 0 ];then
        echo 'export PATH="$HOME/aes-tool-linuxv1.2.0/:$PATH"' >> ~/.bashrc # run it ...2
        source ~/.bashrc # run it ...3
        if [ $? -eq 0 ];then
                echo "Operation success!"
        else
                echo "Operation faild!"
        fi
else
        echo "Operation faild!"
fi

