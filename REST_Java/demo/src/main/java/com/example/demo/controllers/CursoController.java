package com.example.demo.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.Optional;
import com.example.demo.models.Curso;
import com.example.demo.repositories.CursoRepository;

@RestController
@RequestMapping("/api/cursos")
@CrossOrigin(origins = "*")
public class CursoController {

    @Autowired
    private CursoRepository cursoRepository;

    // 1. REGISTRAR
    @PostMapping
    public Curso registrar(@RequestBody Curso curso) {
        return cursoRepository.save(curso);
    }

    // 2. BUSCAR UNO (Por nombre)
    @GetMapping("/buscar")
    public ResponseEntity<?> buscar(@RequestParam String nombre) {
        Optional<Curso> curso = cursoRepository.findByNombre(nombre);
        if (curso.isPresent()) return ResponseEntity.ok(curso.get());
        return ResponseEntity.status(404).body("❌ Curso no encontrado.");
    }

    // 3. EDITAR
    @PutMapping("/editar")
    public String editar(@RequestParam String buscar, @RequestBody Curso datos) {
        Optional<Curso> existe = cursoRepository.findByNombre(buscar);
        if (existe.isPresent()) {
            Curso c = existe.get();
            c.setNombre(datos.getNombre());
            c.setFechaInicio(datos.getFechaInicio());
            c.setCreditos(datos.getCreditos());
            cursoRepository.save(c);
            return "✅ Actualizado: " + datos.getNombre();
        }
        return "❌ Error: Curso no existe.";
    }

    // 4. ELIMINAR UNO
    @DeleteMapping("/eliminar")
    public String eliminarUno(@RequestParam String nombre) {
        Optional<Curso> existe = cursoRepository.findByNombre(nombre);
        if (existe.isPresent()) {
            cursoRepository.delete(existe.get());
            return "🗑️ Eliminado: " + nombre;
        }
        return "⚠️ No existe.";
    }

    // 5. ELIMINAR TODOS
    @DeleteMapping("/eliminar-todos")
    public String eliminarTodos() {
        long count = cursoRepository.count();
        cursoRepository.deleteAll();
        return "🔥 Se borraron " + count + " cursos.";
    }

    // 6. BUSCAR TODOS (NUEVO)
    @GetMapping("/todos")
    public Iterable<Curso> listarTodos() {
        return cursoRepository.findAll();
    }
}