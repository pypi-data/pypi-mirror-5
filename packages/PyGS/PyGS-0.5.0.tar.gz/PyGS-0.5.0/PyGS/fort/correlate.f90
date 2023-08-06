!============================================================================
!4. 2P Correlate (Data set with itself)
!============================================================================ 	 
subroutine correlation_dd(nr,end_r,n,pos1,r,n_cores)
	use omp_lib
	implicit none
	
 	!!! INTENT IN !!!!!!!!
 	integer, intent(in)		:: nR			!Number of separation bins
	integer, intent(in)		:: N			!Number of objects
	real(8), intent(in)		:: pos1(3,N)	!Cartesian Positions of particles
	real(8), intent(in)		:: end_r		!The largest separation calculated.
	integer, intent(in)     :: n_cores
	
	!!! INTENT OUT !!!!!!!
	real(8),intent(out)				:: R(nr)			!The binned data.

	!!! LOCAL !!!!!!!!!!!!
	integer				:: i, i_b,j		!Iterators
	real(8)				:: d			!Distance between particles.
	real(8)				:: dr
	R(:) = 0.d0
	dr = end_r/nr
	
	!Perform the separation binning
	!$OMP parallel do private(i_b,d,i) NUM_THREADS(n_cores) schedule(dynamic,N/100)
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
subroutine correlation_dr(nr,end_r,n,pos1,n2,pos2,r,n_cores)
	use omp_lib
	implicit none
	
 	integer, intent(in)		:: nR			!Number of separation bins
	integer, intent(in)		:: N			!Number of objects
	integer, intent(in)		:: N2			!Number of objects in second group
	real(8), intent(in)		:: pos1(3,N)	!Cartesian Positions of particles
	real(8), intent(in)		:: pos2(3,N2)	!Cartesian Positions of second group
	real(8), intent(in)		:: end_r		!The largest separation calculated.
	integer, intent(in)     :: n_cores
	
	real(8), intent(out)	:: R(nr)		!The binned data.

	integer		:: i, i_b,j		!Iterators
	real*8		:: d			!Distance between particles.
	real*8		:: dr
	
	
	R(:) = 0.d0
	dr = end_r/nr
	!Perform the separation binning
	!$OMP parallel do private(i_b,d,i) NUM_THREADS(n_cores) schedule(dynamic,N/100)
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



!============================================================================
!4. 2P Correlate (Data set with itself)
!============================================================================
subroutine correlation_dd_1d(nr,end_r,n,pos1,r,n_cores)
    use omp_lib
    implicit none
    !**** WE ASSUME THAT pos1 is sorted in ascending order!!!!

    !!! INTENT IN !!!!!!!!
    integer, intent(in)     :: nr          !Number of separation bins
    integer, intent(in)     :: N            !Number of objects
    real(8), intent(in)     :: pos1(N)    !Cartesian Positions of particles
    real(8), intent(in)     :: end_r        !The largest separation calculated.
    integer, intent(in)     :: n_cores

    !!! INTENT OUT !!!!!!!
    real(8),intent(out)             :: r(nr)            !The binned data.

    !!! LOCAL !!!!!!!!!!!!
    integer             :: i, i_b,j     !Iterators
    real(8)             :: d            !Distance between particles.
    real(8)             :: dr
    R(:) = 0.d0
    dr = end_r/nr

    write(*,*) "Len of r: ", size(r), nr
    write(*,*) "end_r:", end_r
    write(*,*) "Number of data: ", size(pos1), N
    write(*,*) "Number of cores: ", n_cores

    !Perform the separation binning
    !$OMP parallel do private(i_b,d,i) NUM_THREADS(n_cores) schedule(dynamic,N/1000)
    do j=1,N-1
        do i_b=j+1,N
            d=pos1(i_b)-pos1(j) !d will always be positive because of ordering.
            if(d.LT.end_r)then
                i = Floor(d/dr)+1
                !$OMP atomic
                r(i) = r(i)+2.d0
            else
                exit
            end if
        end do
    end do
    !$OMP end parallel do

    write(*,*) "DONE DD FROM INSIDE"
end subroutine

!============================================================================
!4. 2P Correlate (Different Datasets)
!============================================================================
subroutine correlation_dr_1d(nr,end_r,n,pos1,n2,pos2,r,n_cores)
    use omp_lib
    implicit none
    !**** WE ASSUME THAT pos1 and pos2 are sorted in ascending order!!!!


    integer, intent(in)     :: nR           !Number of separation bins
    integer, intent(in)     :: N            !Number of objects
    integer, intent(in)     :: N2           !Number of objects in second group
    real(8), intent(in)     :: pos1(N)    !Cartesian Positions of particles
    real(8), intent(in)     :: pos2(N2)   !Cartesian Positions of second group
    real(8), intent(in)     :: end_r        !The largest separation calculated.
    integer, intent(in)     :: n_cores

    real(8), intent(out)    :: r(nr)        !The binned data.

    integer     :: i, i_b,j     !Iterators
    real*8      :: d            !Distance between particles.
    real*8      :: dr


    r(:) = 0.d0
    dr = end_r/nr
    !Perform the separation binning
    !$OMP parallel do private(i_b,d,i) NUM_THREADS(n_cores) schedule(dynamic,N/1000)
    do j=1,N
        do i_b=1,N2
            d=pos2(i_b)-pos1(j)
            if(abs(d).LT.end_r)then
                i = Floor(abs(d)/dr)+1
                !$OMP atomic
                r(i) = r(i)+1.d0
            elseif(d.gt.0)then
                exit
            end if

        end do
    end do
    !$OMP end parallel do

    write(*,*) "Finished DR from inside"
end subroutine

