module lumfunc_denom
    implicit none

    contains

    subroutine denom(Np,ngal,bins,phi,deltaM,absmagmax,denominator)
        !Calculates denom (as a whole) of eq.1.28
        integer, intent(in) :: Np !Number of bins in lum func
        integer, intent(in) :: ngal !Number of galaxies
        real(8), intent(in) :: bins(Np+1) !The bin edges of the lum func
        real(8), intent(in) :: phi(Np) !The previous version of the lum func
        real(8), intent(in) :: deltaM !The bin width
        real(8), intent(in) :: absmagmax(ngal) !the maximum absolute mag at redshift of the galaxy
        
        real(8), intent(out):: denominator(Np) !The denominator of eq 1.28 of Jake's description
        
        real(8) :: top, bottom
        integer :: m,i
        denominator = 0.d0

        write(*,*) "Number of bins: ", Np
        write(*,*) "Number of galaxies: ", ngal
        write(*,*) "Bins go from ", minval(bins), " to ", maxval(bins)
        write(*,*) "Minimum and maximum of phi: ", minval(phi), maxval(phi)
        write(*,*) "delta M: ", deltaM
        write(*,*) "min and max of absmagmax", minval(absmagmax), maxval(absmagmax)

        do i=1,ngal
            if (isnan(absmagmax(i)))then
                write(*,*) i
            end if
        end do
        do m=1,Np
            do i=1,ngal
                call H(absmagmax(i)-(bins(m)+deltaM/2.0),deltaM,top)            
                call denom_of_denom(absmagmax(i),bins(1),deltaM,Np,phi,bottom)
                denominator(m) = denominator(m) + top/bottom
                
                !if (bottom == 0) then
                !    write(*,*) m,i, bottom, top
                !end if
            end do
            
        end do
            
            
    end subroutine


    subroutine H(diff,deltaM,x)
        !The function H() from eq. 1.23 of Jake's MLE explanation
        real(8), intent(in) :: diff, deltaM

        real(8), intent(out) :: x
        if (diff .le. -deltaM/2.0)then
            x = 0.d0
        else if (diff .gt. deltaM/2.0)then
            x= 1.d0
        else
            x =  diff/deltaM + 0.5d0
        end if
    end subroutine

    subroutine denom_of_denom(absmagmax,min_M,deltaM,Np,phi,H)
        !Calculates denom of denom of eq.1.28
        real(8), intent(in) :: absmagmax, min_M, deltaM
        integer, intent(in) :: Np
        real(8), intent(in) :: phi(:)

        real(8), intent(out):: H

        integer :: the_bin
        real(8) :: centre

        the_bin = floor((absmagmax - min_M)/deltaM)+1
        if(the_bin .le. Np .and. the_bin .ge. 1)then        
            centre = min_M + the_bin*deltaM - deltaM/2.0        
            H = (absmagmax - centre)/deltaM + 0.5d0
            if (the_bin .lt. Np-1)then            
                H = phi(the_bin)*H * sum(phi(the_bin+1:Np)) * deltaM
            else if (the_bin .eq. Np-1)then
                H = phi(the_bin)*H * phi(Np) * deltaM
            else
                H = phi(the_bin)*H * deltaM
            end if
        else if (the_bin .gt. Np)then
            H = sum(phi)*deltaM
        
        else
            continue
        !    write(*,*) the_bin, min_M, absmagmax, deltaM
        end if
        !if (H==0.d0)then
        !    write(*,*) phi(the_bin), sum(phi(the_bin+1:Np)), deltaM
        !end if
    end subroutine

end module