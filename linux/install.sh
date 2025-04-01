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

# extract your zip file then we move 'aes-tool' binray in /usr/bin directory for act as terminal tool
# first enter that directory if you do it manually
# run that line and your done
sudo cp aes-tool /usr/bin/
if [ $? -eq 0 ];then
	echo "Operation success!"
else
	echo "Operation faild!"
fi
# you can remove this directory
