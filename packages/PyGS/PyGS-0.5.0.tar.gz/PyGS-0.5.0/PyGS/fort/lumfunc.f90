module lumfunc_denom
    implicit none

    contains

    subroutine denom(Np,ngal,phi,deltaM,Hmat,denominator)
        !Calculates denom (as a whole) of eq.1.28
        integer, intent(in) :: Np !Number of bins in lum func
        integer, intent(in) :: ngal !Number of galaxies
        real(8), intent(in) :: phi(Np) !The previous version of the lum func
        real(8), intent(in) :: deltaM !The bin width
        real(8), intent(in) :: Hmat(ngal,Np) !The H matrix
        real(8), intent(out):: denominator(Np) !The denominator of eq 1.28 of Jake's description
        
        real(8) :: bottom
        integer :: j,i
        denominator = 0.d0

        do j=1,Np
            do i=1,ngal
                call denom_of_denom(Np,phi,Hmat(i,:),deltaM,bottom)
                denominator(j) = denominator(j) + Hmat(i,j)/bottom
            end do
        end do
    end subroutine

    subroutine get_hmatrix(Np, ngal, absmagmax,bins,deltaM,HMAT)
        !Calculates a single constant H matrix - an entry for each
        !galaxy and each bin
        integer, intent(in) :: Np, ngal !Number of galaxies and bins
        real(8), intent(in) :: absmagmax(ngal)
        real(8), intent(in) :: bins(Np+1) !The bin edges of the lumfunc
        real(8), intent(in) :: deltaM !Bin width

        real(8), intent(out) :: HMAT(ngal,Np) !The H matrix

        integer :: i,j

        do i=1,ngal
            do j=1,Np
                call H(absmagmax(i)-(bins(j)+deltaM/2.0),deltaM,HMAT(i,j))
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

    subroutine denom_of_denom(Np,phi,Hvec,deltaM,bottom)
        !Calculates denom of denom of eq.1.28

        real(8), intent(in) :: deltaM
        integer, intent(in) :: Np
        real(8), intent(in) :: phi(Np)
        real(8), intent(in) :: Hvec(Np)
        real(8), intent(out):: bottom

        integer :: i

        bottom = 0.d0
        do i=1,Np
            bottom = bottom + phi(i)*Hvec(i)*deltaM
        end do

!        the_bin = floor((absmagmax - min_M)/deltaM)+1
!        if(the_bin .le. Np .and. the_bin .ge. 1)then
!            centre = min_M + the_bin*deltaM - deltaM/2.0
!            H = (absmagmax - centre)/deltaM + 0.5d0
!            if (the_bin .lt. Np-1)then
!                H = phi(the_bin)*H * sum(phi(the_bin+1:Np)) * deltaM
!            else if (the_bin .eq. Np-1)then
!                H = phi(the_bin)*H * phi(Np) * deltaM
!            else
!                H = phi(the_bin)*H * deltaM
!            end if
!        else if (the_bin .gt. Np)then
!            H = sum(phi)*deltaM
!
!        else
!            continue
!        !    write(*,*) the_bin, min_M, absmagmax, deltaM
!        end if
!        !if (H==0.d0)then
!        !    write(*,*) phi(the_bin), sum(phi(the_bin+1:Np)), deltaM
!        !end if
    end subroutine

end module
