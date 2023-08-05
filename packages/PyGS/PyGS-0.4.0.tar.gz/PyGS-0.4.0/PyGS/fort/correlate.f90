!============================================================================
!4. 2P Correlate (Data set with itself)
!============================================================================ 	 
subroutine correlation_dd(nr,end_r,n,pos1,r)
	use omp_lib
	implicit none
	
 	!!! INTENT IN !!!!!!!!
 	integer, intent(in)		:: nR			!Number of separation bins
	integer, intent(in)		:: N			!Number of objects
	real(8), intent(in)		:: pos1(3,N)	!Cartesian Positions of particles
	real(8), intent(in)		:: end_r		!The largest separation calculated.
	
	
	!!! INTENT OUT !!!!!!!
	real(8),intent(out)				:: R(nr)			!The binned data.

	!!! LOCAL !!!!!!!!!!!!
	integer				:: i, i_b,j		!Iterators
	real(8)				:: d			!Distance between particles.
	real(8)				:: dr
	R(:) = 0.d0
	dr = end_r/nr
	
	!Perform the separation binning
	!$OMP parallel do private(i_b,d,i) schedule(dynamic,N/100)
	do j=1,N-1
		do i_b=j+1,N
			if(abs(pos1(1,j)-pos1(1,i_b)).GT.end_r)then
		 		cycle
		 	else if(abs(pos1(2,j)-pos1(2,i_b)).GT.end_r)then
		 		cycle
		 	else if(abs(pos1(3,j)-pos1(3,i_b)).GT.end_r)then
		 		cycle
		 	end if
		 	d=(pos1(1,j)-pos1(1,i_b))**2+&
		 		&(pos1(2,j)-pos1(2,i_b))**2+&
		 		&(pos1(3,j)-pos1(3,i_b))**2
		 	if(d.LT.end_r**2)then
		 		d = Sqrt(d)
		 		i = Floor(d/dr)+1
		 		!$OMP atomic
		 		R(i) = R(i)+2.d0
		 	end if
		end do
	end do
	!$OMP end parallel do
	
end subroutine

!============================================================================
!4. 2P Correlate (Different Datasets)
!============================================================================ 	 
subroutine correlation_dr(nr,end_r,n,pos1,n2,pos2,r)
	use omp_lib
	implicit none
	
 	integer, intent(in)		:: nR			!Number of separation bins
	integer, intent(in)		:: N			!Number of objects
	integer, intent(in)		:: N2			!Number of objects in second group
	real(8), intent(in)		:: pos1(3,N)	!Cartesian Positions of particles
	real(8), intent(in)		:: pos2(3,N2)	!Cartesian Positions of second group
	real(8), intent(in)		:: end_r		!The largest separation calculated.
	
	
	real(8), intent(out)	:: R(nr)		!The binned data.

	integer		:: i, i_b,j		!Iterators
	real*8		:: d			!Distance between particles.
	real*8		:: dr
	
	
	R(:) = 0.d0
	dr = end_r/nr
	!Perform the separation binning
	!$OMP parallel do private(i_b,d,i) schedule(dynamic,N/100)
	do j=1,N
		do i_b=1,N2
	 		if(abs(pos1(1,j)-pos2(1,i_b)).GT.end_r)then
	 			cycle
	 		else if(abs(pos1(2,j)-pos2(2,i_b)).GT.end_r)then
	 			cycle
	 		else if(abs(pos1(3,j)-pos2(3,i_b)).GT.end_r)then
	 			cycle
	 		end if
	 		d=(pos1(1,j)-pos2(1,i_b))**2+&
	 			&(pos1(2,j)-pos2(2,i_b))**2+&
	 			&(pos1(3,j)-pos2(3,i_b))**2
	 		if(d.LT.end_r**2)then
	 			d = Sqrt(d)
	 			i = Floor(d/dr)+1
	 			!$OMP atomic
	 			R(i) = R(i)+1.d0
	 		end if
	 	end do
	end do
	!$OMP end parallel do

end subroutine



