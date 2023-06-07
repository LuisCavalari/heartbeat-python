import time
import multiprocessing
from domain.heart_beat import HeartbeatProcess
import argparse

# Função para iniciar o HeartbeatProcess
def start_heartbeat_process(process_name, send_interval, receive_interval):
    heartbeat_process = HeartbeatProcess(process_name, send_interval, receive_interval)
    heartbeat_process.start()

if __name__ == '__main__':
    # Recupera os argumentos de linha de comando sobre a quantidade de processos desejada
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-n','--numbers_of_processes', required=True, help="Numero de processo")
    args = vars(argument_parser.parse_args())
    N = int(args['numbers_of_processes'])
    processes = []
    # Criação dos processos
    for index in range(1, N+1):
        processes.append(multiprocessing.Process(target=start_heartbeat_process, args=(f"Processo{index}", 3, 1)))

    print('Iniciando process os processos...')
    # Inicialização dos processos
    for process in processes:
        process.start()
    try:
        # Mantém a função principal em execução
        print('Processos OK')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Interrompe a execução dos processos ao pressionar Ctrl+C
        for process in processes:
            process.terminate()
            process.join()
