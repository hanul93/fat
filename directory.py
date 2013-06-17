# -*- coding:utf-8 -*-

import struct

def GetTime(t, tenth) :
	t_h = 0xF800
	t_m = 0x07E0
	t_s = 0x001F
	
	h = (t & t_h) >> 11
	m = (t & t_m) >> 5
	s = (t & t_s) * 2 
	s = s + (tenth * 0.01)
	
	return '%02d:%02d:%02d' % (h, m, s)

def GetDate(t) :
	t_y = 0xFE00
	t_m = 0x01E0
	t_d = 0x001F
	
	y = (t & t_y) >> 9
	y += 1980
	m = (t & t_m) >> 5
	d = (t & t_d)  
	
	return '%04d-%02d-%02d' % (y, m, d)

def GetFileName_SFN(entry) :	
	name = entry[0:8]
	name = name.strip()

	ext  = entry[8:8+3]
	ext  = ext.strip()
	if len(ext) != 0 :
		ext = '.' + ext 
		
	return name+ext
	
def GetFileName_LFN(entry) :
	num = len(entry) / 0x20
	
	name = ''
	
	for i in range(num-1) :
		name1 = entry[(i*0x20)+1:(i*0x20)+0xB]
		name2 = entry[(i*0x20)+0xE:(i*0x20)+0x1A]
		name3 = entry[(i*0x20)+0x1C:(i*0x20)+0x20]
		t_name = name1+name2+name3
		
		name = t_name + name
			
	name = name.replace(chr(0xff), '').decode('utf-16').strip()
	name = name.replace(chr(0x00), '')

	return name
	
def GetFileName(entry) :
	num = len(entry) / 0x20
	
	if num == 1 :
		name = GetFileName_SFN(entry)
	else :
		name = GetFileName_LFN(entry)
	
	return name 
	
fp = open('\\\\.\\E:', 'rb')
fp.seek(0xCF000)
dir = fp.read(0x200)

t_entry = ''

for i in range(0x200/0x20) :
	entry = dir[i*0x20:(i+1)*0x20]
	if ord(entry[0]) != 0x00 : # 빈 파일명이 아님
		if ord(entry[0]) != 0xE5 : # 삭제가 아니고
			if ord(entry[11]) == 0x0F :
				# 긴파일명
				t_entry += entry
			else : # 짧은명
				t_entry += entry
				
				name = GetFileName(t_entry)
				
				ct = struct.unpack('<H', entry[14:14+2])[0]
				tenth = ord(entry[13])
				str_time = GetTime(ct, tenth)				
					
				cd = struct.unpack('<H', entry[16:16+2])[0]
				str_date = GetDate(cd)	
				
				s = '%s  %s     %s' % (str_date, str_time, name)
				
				print s
				
				t_entry = '' # 최종 작업이 끝났으니 엔트리 변수는 초기화

fp.close()

