import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_URL = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  registrarFoco(dados: any): Observable<any> {
    return this.http.post(`${this.API_URL}/registro-foco`, dados);
  }

  getDiagnostico(): Observable<any> {
    return this.http.get(`${this.API_URL}/diagnostico-produtividade`);
  }
}