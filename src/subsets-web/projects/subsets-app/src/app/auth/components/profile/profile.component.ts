import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgTinyUrlService } from 'ng-tiny-url';
import { AuthService } from '../../../core/service/auth.service';
import { NotificationService } from '../../../core/service/notification.service';
import { SharedService } from '../../../core/service/shared.service';

@Component({
  selector: 'alliance-cgiar-org-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
})
export class ProfileComponent implements OnInit {
  @Input()
  public photoUrl!: string;

  /*  @Input()
  public name!: string; */

  public showInitials = false;
  public initials!: string;
  public circleColor!: string;
  shortenedUrl:any;

  private colors = [
    '#EB7181', // red
    '#468547', // green
    '#FFD558', // yellow
    '#3670B2', // blue
  ];
  actualPage: any;
  headers: any;
  username!: any;
  subsets$: any = [];
  constructor(
    private _authService: AuthService,
    private _sharedService: SharedService,
    private router: Router,
    private notifyService: NotificationService,
    private tinyUrl: NgTinyUrlService
  ) {
    this.headers = ['Name', 'Action'];
  }

  ngOnInit(): void {
    this.getSubsetsByUser();
    this.username = localStorage.getItem('username');
    if (!this.photoUrl) {
      this.showInitials = true;
      this.createInititals();

      const randomIndex = Math.floor(
        Math.random() * Math.floor(this.colors.length)
      );
      this.circleColor = this.colors[randomIndex];
    }
  }

  copyInputMessage(obj: any, uri: any) {
    let url:any;
    if (obj.includes('|')) {
      let parms = obj.split('|');
      url = this.router.createUrlTree([
        '/explore/filter/',
        { passport: parms[0], indicator: parms[1] },
      ]);
    } else {
      url = this.router.createUrlTree([
        '/explore/filter/',
        { passport: obj },
      ]);
    }
    this.tinyUrl.shorten(uri + url.toString()).subscribe((res:string) => {
      this.shortenedUrl = res;
      const selBox = document.createElement('textarea');
      selBox.style.position = 'fixed';
      selBox.style.left = '0';
      selBox.style.top = '0';
      selBox.style.opacity = '0';
      selBox.value = this.shortenedUrl;
      document.body.appendChild(selBox);
      selBox.focus();
      selBox.select();
      document.execCommand('copy');
      document.body.removeChild(selBox);
      this.notifyService.showInfo('URL copied in the clipboard', 'Info');
    });

  }

  go(obj: any) {
    if (obj.includes('|')) {
      let parms = obj.split('|');
      let url = this.router.createUrlTree([
        '/explore/filter/',
        { passport: parms[0], indicator: parms[1] },
      ]);
      window.open(url.toString(), '_blank');
    } else {
      let url = this.router.createUrlTree([
        '/explore/filter/',
        { passport: obj },
      ]);
      window.open(url.toString(), '_blank');
    }
  }

  getSubsetsByUser = () => {
    this._authService.getSubsets().subscribe(
      (res: any) => {
        this.subsets$ = res;
        console.log(res);
      },
      (err: any) => console.log(err)
    );
  };

  private createInititals(): void {
    let initials = '';
    for (let i = 0; i < this.username.length; i++) {
      if (this.username.charAt(i) === ' ') {
        continue;
      }

      if (this.username.charAt(i) === this.username.charAt(i)) {
        initials += this.username.charAt(i);

        if (initials.length == 2) {
          break;
        }
      }
    }

    this.initials = initials;
  }
}
