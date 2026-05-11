import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './services/api';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule], // Importante para o [(ngModel)] funcionar
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {
  registro = {
    nivel_foco: 5,
    tempo_minutos: 30,
    comentario: '',
    categoria: 'Desenvolvimento'
  };

  diagnostico: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.atualizarDiagnostico();
  }

  enviar() {
  this.apiService.registrarFoco(this.registro).subscribe({
    next: (res) => {
      // Opcional: Mostrar um feedback visual rápido
      console.log('Registro salvo!', res);
      
      // função que busca o diagnóstico assim que o POST termina com sucesso
      this.atualizarDiagnostico(); 

      // Limpar o campo de comentário para o próximo registro
      this.registro.comentario = '';
    },
    error: (err) => {
      alert('Erro ao salvar sessão. Verifique se o backend está rodando!');
      console.error(err);
    }
  });
}

atualizarDiagnostico() {
  this.apiService.getDiagnostico().subscribe({
    next: (res) => {
      // Ao atribuir o resultado à variável, o Angular atualiza o HTML automaticamente
      this.diagnostico = res; 
    },
    error: (err) => {
      console.error('Erro ao buscar diagnóstico', err);
    }
  });
  }
}