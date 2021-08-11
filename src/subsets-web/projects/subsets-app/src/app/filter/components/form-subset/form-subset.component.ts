import { Component, Inject, OnInit, AfterContentInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AuthService } from '../../../core/service/auth.service';
import { SharedService } from '../../../core/service/shared.service';
import { Router } from '@angular/router';
import { NotificationService } from '../../../core/service/notification.service';

@Component({
  selector: 'alliance-cgiar-org-form-subset',
  templateUrl: './form-subset.component.html',
  styleUrls: ['./form-subset.component.scss'],
})
export class FormSubsetComponent implements OnInit, AfterContentInit {
  subset$: any;
  passportParameters$: any;
  indicatorsParameters$: any;
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<FormSubsetComponent>,
    private _authService: AuthService,
    private _sharedService: SharedService,
    private router: Router,
    private notifyService : NotificationService
  ) { 
    this.subset$ = {
      description: '',
      url: '',
      params: '',
      user: '',
    };
  }

  ngAfterContentInit() {
  }

  ngOnInit(): void {
  }

  close() {
    this.dialogRef.close();
  }

  storeSubset = () => {
    this.subset$.url = location.origin
    console.log(location.origin)
    if (this.data.indicatorParams) {
      this.subset$.params = JSON.stringify(this.data.passportParams) + "|" + JSON.stringify(this.data.indicatorParams);
    }else {
      this.subset$.params = JSON.stringify(this.data.passportParams);
    }
    this.subset$.user = localStorage.getItem('username');
    this._authService.AddSubset(this.subset$).subscribe((res: any) => {
      console.log(res);
      this.notifyService.showSuccess("Successfully stored subset", "Success")
      this.close()
    }),
      (err: any) => console.log(err);
  };
}
