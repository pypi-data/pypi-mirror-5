c                                                                      
c     this program reads a level 3 daily gridded ascii data file 
c     for the day specified.  the variables lat and lon contain the 
c     latitudes and longitudes of the center of each of the grid    
c     cells in the array ozone.                                    
c                          
      subroutine reader_n7t(filename, dt, lon, lat, ozone)                                       
      character*80   header
      character*80   filename
      character*12, intent(OUT)::   dt                               
      real*4, intent(OUT)::      ozone                                      
      real*4, intent(OUT)::         lat(180), lon(288)                        
                                                              
      dimension      ozone(288,180)                          
c                                                           
c     calculate latitudes and longitudes                   
c                                                         
      dlat = 1.0                                         
      do 10 i=1,180                                     
      lat(i) = -89.5 + (i-1)*dlat                      
10    continue                                        
      dlon = 1.25                                    
      do 20 i=1,288                                 
      lon(i) = -179.375 + (i-1)*dlon               
20    continue                                    
c
c     get the name of the file
c     write (6,*) 'What is the name of the input file?'
c     read (5,'(a80)') filename
c    
c     find the actual length of the filename
c
      len = index(filename,' ') - 1
c                                                
c     open the input file                       
c                                              
      open(1,file=filename(1:len),status='old')               
c                                                           
c     read in the header lines (this particular code does not 
c     do anything with the information in the header)
c                                                         
      read(1,'(a80)') header                             
      dt = header(11:23)
      read(1,'(a80)') header                            
      read(1,'(a80)') header                           
c                                                     
c     read in the data into the array ozone          
c                                                   
      do 30 i=1,180                                
      read(1,'(1x,25F3.0)') (ozone(j,i),j=1,288)    
30    continue                                                                
c                                                             
c     close the input file                                   
c                                                           
      close(1)                                             
c                                                         
c     process/print the ozone data                       
c                                                       
      end subroutine
